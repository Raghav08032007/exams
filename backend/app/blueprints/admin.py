"""
/admin blueprint — paper upload, verification queue, and statistics dashboard.
All write routes require admin or verifier role (JWT + role check).
Uses raw PyMySQL queries — no ORM. No scraper code.
"""
import os
import uuid
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import get_db
from ..utils.auth_helpers import admin_required, verifier_or_admin_required
from ..utils.file_validators import validate_pdf_upload, validate_image_upload

admin_bp = Blueprint("admin", __name__)


def _get_or_create_subject(name: str, conn) -> int:
    """Return the subject ID for name, creating the row if it doesn't exist."""
    name = name.strip()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM subjects WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
        return cur.lastrowid


def _notify_new_paper(conn, paper_id: int, title: str, exam_name: str, year: int, exam_slug: str):
    """Create a broadcast notification for all users when a new paper is published."""
    notif_title = f"📄 New Paper Added: {exam_name} ({year})"
    notif_msg = f"New {exam_name} paper '{title}' ({year}) is now available in ExamVault!"
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notifications (user_id, title, message, paper_id, exam_slug)
                VALUES (NULL, %s, %s, %s, %s)
                """,
                (notif_title, notif_msg, paper_id, exam_slug),
            )
        conn.commit()
    except Exception as e:
        print(f"Failed to create notification: {e}")


def _paper_to_dict(row: dict) -> dict:
    """Serialize an admin paper row (with joined category/exam data)."""
    data = {
        "id":                  row["id"],
        "exam_category_id":    row["exam_category_id"],
        "year":                row["year"],
        "session":             row.get("session"),
        "title":               row["title"],
        "language":            row.get("language", "English"),
        "pdf_url":             row.get("pdf_url"),
        "cover_image_url":     row.get("cover_image_url"),
        "file_size":           row.get("file_size"),
        "has_answer_key":      bool(row.get("has_answer_key", False)),
        "answer_key_pdf_url":  row.get("answer_key_pdf_url"),
        "upload_date":         row["upload_date"].isoformat() if row.get("upload_date") else None,
        "download_count":      row.get("download_count", 0),
        "verification_status": row.get("verification_status"),
        "verified_by":         row.get("verified_by"),
        "uploaded_by":         row.get("uploaded_by"),
        "rejection_note":      row.get("rejection_note"),
        "subjects":            [],
    }
    if row.get("category_name"):
        data["category"] = {
            "id":      row.get("category_id"),
            "exam_id": row.get("exam_id_join"),
            "name":    row.get("category_name"),
            "slug":    row.get("category_slug"),
        }
    if row.get("exam_name"):
        data["exam"] = {
            "id":               row.get("exam_id_join"),
            "name":             row.get("exam_name"),
            "slug":             row.get("exam_slug"),
            "accent_color_hex": row.get("accent_color_hex"),
        }
    return data


_ADMIN_PAPER_SELECT = """
    SELECT
        p.id, p.exam_category_id, p.year, p.session, p.title, p.language,
        p.pdf_url, p.cover_image_url, p.file_size, p.has_answer_key, p.answer_key_pdf_url,
        p.upload_date, p.download_count, p.verification_status,
        p.verified_by, p.uploaded_by, p.rejection_note,
        ec.id   AS category_id,
        ec.name AS category_name,
        ec.slug AS category_slug,
        ec.exam_id AS exam_id_join,
        e.name  AS exam_name,
        e.slug  AS exam_slug,
        e.accent_color_hex
    FROM papers p
    JOIN exam_categories ec ON p.exam_category_id = ec.id
    JOIN exams e ON ec.exam_id = e.id
"""


@admin_bp.route("/papers", methods=["POST"])
@verifier_or_admin_required
def upload_paper():
    """
    POST /admin/papers
    Multipart form-data fields:
      file             (required) — PDF file
      title            (required) — paper title
      exam_category_id (required) — FK to exam_categories
      year             (required) — 4-digit year
      session          (optional) — e.g. "January Session 1"
      language         (optional, default 'English')
      subjects         (optional) — comma-separated subject names
      cover_image      (optional) — Image file (.png, .jpg, .webp)
      answer_key       (optional) — PDF file for answer key
    Returns: { "paper": {...} }
    """
    raw_id = get_jwt_identity()
    current_user_id = int(raw_id) if raw_id is not None else None

    title            = (request.form.get("title") or "").strip()
    exam_category_id = request.form.get("exam_category_id", type=int)
    year             = request.form.get("year", type=int)
    session          = (request.form.get("session") or "").strip() or None
    language         = (request.form.get("language") or "English").strip()
    subjects_raw     = (request.form.get("subjects") or "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400
    if not exam_category_id:
        return jsonify({"error": "exam_category_id is required"}), 400
    if not year or year < 1990 or year > 2035:
        return jsonify({"error": "year must be a valid 4-digit year (1990–2035)"}), 400

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM exam_categories WHERE id = %s", (exam_category_id,))
        if not cur.fetchone():
            return jsonify({"error": f"exam_category_id {exam_category_id} not found"}), 404

    # Validate optional main PDF
    pdf_file = request.files.get("file")
    valid, err = validate_pdf_upload(pdf_file, required=False)
    if not valid:
        return jsonify({"error": err}), 400

    # Validate optional cover image
    cover_image_file = request.files.get("cover_image")
    valid_img, err_img = validate_image_upload(cover_image_file)
    if not valid_img:
        return jsonify({"error": f"Cover image: {err_img}"}), 400

    # Validate optional answer key
    answer_key_file = request.files.get("answer_key")
    if answer_key_file and answer_key_file.filename:
        valid_ak, err_ak = validate_pdf_upload(answer_key_file, required=True)
        if not valid_ak:
            return jsonify({"error": f"Answer key: {err_ak}"}), 400

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    # Save main PDF if provided
    pdf_url = None
    file_size = 0
    if pdf_file and pdf_file.filename:
        unique_name = f"{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(upload_dir, unique_name)
        pdf_file.seek(0, os.SEEK_END)
        file_size = pdf_file.tell()
        pdf_file.seek(0)
        pdf_file.save(pdf_path)
        pdf_url = f"/uploads/{unique_name}"

    # Save optional cover image if provided
    cover_image_url = None
    if cover_image_file and cover_image_file.filename:
        ext = cover_image_file.filename.rsplit(".", 1)[1].lower() if "." in cover_image_file.filename else "png"
        img_name = f"cover_{uuid.uuid4().hex}.{ext}"
        img_path = os.path.join(upload_dir, img_name)
        cover_image_file.save(img_path)
        cover_image_url = f"/uploads/{img_name}"

    # Save answer key if provided
    has_answer_key     = False
    answer_key_pdf_url = None
    if answer_key_file and answer_key_file.filename:
        ak_name = f"ak_{uuid.uuid4().hex}.pdf"
        ak_path = os.path.join(upload_dir, ak_name)
        answer_key_file.save(ak_path)
        answer_key_pdf_url = f"/uploads/{ak_name}"
        has_answer_key = True

    # Insert paper record — auto-verify admin uploads so they are immediately viewable by all users
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO papers
              (exam_category_id, year, session, title, language,
               pdf_url, cover_image_url, file_size, download_count, has_answer_key, answer_key_pdf_url,
               verification_status, verified_by, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, 'verified', %s, %s)
            """,
            (
                exam_category_id, year, session, title, language,
                pdf_url, cover_image_url, file_size, has_answer_key, answer_key_pdf_url,
                current_user_id, current_user_id,
            ),
        )
        paper_id = cur.lastrowid

        # Attach subjects
        if subjects_raw:
            for s_name in subjects_raw.split(","):
                s_name = s_name.strip()
                if s_name:
                    subject_id = _get_or_create_subject(s_name, conn)
                    cur.execute(
                        "INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)",
                        (paper_id, subject_id),
                    )

        conn.commit()

        # Fetch the newly created paper
        cur.execute(f"{_ADMIN_PAPER_SELECT} WHERE p.id = %s", (paper_id,))
        paper_row = cur.fetchone()

        if paper_row:
            _notify_new_paper(
                conn,
                paper_id,
                paper_row.get("title", title),
                paper_row.get("exam_name", "Exam"),
                paper_row.get("year", year),
                paper_row.get("exam_slug", "upsc"),
            )

    return jsonify({
        "message": "Paper uploaded successfully — pending admin verification",
        "paper":   _paper_to_dict(paper_row),
    }), 201


@admin_bp.route("/categories", methods=["POST"])
@verifier_or_admin_required
def create_category():
    """
    POST /admin/categories
    Body: { "exam_slug": "tnpsc", "name": "Group 3" }
    Creates a new category for an exam.
    """
    data = request.get_json(silent=True) or {}
    exam_slug = (data.get("exam_slug") or "").strip().lower()
    name      = (data.get("name") or "").strip()

    if not exam_slug or not name:
        return jsonify({"error": "exam_slug and name are required"}), 400

    import re
    slug = re.sub(r"[^\w]+", "-", name.lower()).strip("-")

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM exams WHERE slug = %s", (exam_slug,))
        exam = cur.fetchone()
        if not exam:
            return jsonify({"error": f"Exam '{exam_slug}' not found"}), 404

        cur.execute(
            """
            INSERT INTO exam_categories (exam_id, name, slug)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name)
            """,
            (exam["id"], name, slug),
        )
        conn.commit()

        cur.execute(
            "SELECT id, exam_id, name, slug FROM exam_categories WHERE exam_id = %s AND slug = %s",
            (exam["id"], slug),
        )
        cat = cur.fetchone()

    return jsonify({"message": "Category created successfully", "category": cat}), 201


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """
    GET /admin/stats
    Returns per-exam download totals and paper counts.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.name, e.slug, e.accent_color_hex,
                   COUNT(p.id)              AS paper_count,
                   COALESCE(SUM(p.download_count), 0) AS total_downloads
            FROM exams e
            LEFT JOIN exam_categories ec ON ec.exam_id = e.id
            LEFT JOIN papers p ON p.exam_category_id = ec.id
            GROUP BY e.id, e.name, e.slug, e.accent_color_hex
            ORDER BY e.name
            """
        )
        rows = cur.fetchall()

    stats = [
        {
            "exam":             r["name"],
            "slug":             r["slug"],
            "accent_color_hex": r["accent_color_hex"],
            "paper_count":      r["paper_count"],
            "total_downloads":  int(r["total_downloads"]),
        }
        for r in rows
    ]
    return jsonify({"stats": stats}), 200


@admin_bp.route("/make-admin", methods=["POST"])
@admin_required
def make_admin():
    """
    POST /admin/make-admin
    Body: { "email": str }
    Promotes a user to admin role.
    """
    data = request.get_json(silent=True)
    if not data or "email" not in data:
        return jsonify({"error": "email is required"}), 400

    email = data["email"].strip().lower()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email, role FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        cur.execute("UPDATE users SET role = 'admin' WHERE id = %s", (user["id"],))
        conn.commit()

    return jsonify({"message": f"{email} is now an admin", "user": {
        "id": user["id"], "name": user["name"], "email": user["email"], "role": "admin"
    }}), 200


@admin_bp.route("/make-verifier", methods=["POST"])
@admin_required
def make_verifier():
    """
    POST /admin/make-verifier
    Body: { "email": str }
    Promotes a user to verifier role.
    """
    data = request.get_json(silent=True)
    if not data or "email" not in data:
        return jsonify({"error": "email is required"}), 400

    email = data["email"].strip().lower()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email, role FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        cur.execute("UPDATE users SET role = 'verifier' WHERE id = %s", (user["id"],))
        conn.commit()

    return jsonify({"message": f"{email} is now a verifier", "user": {
        "id": user["id"], "name": user["name"], "email": user["email"], "role": "verifier"
    }}), 200


@admin_bp.route("/verification-queue", methods=["GET"])
@verifier_or_admin_required
def get_verification_queue():
    """
    GET /admin/verification-queue
    Optional ?status=unverified|verified|rejected (default unverified)
    Returns list of papers for admin review.
    """
    status = request.args.get("status", "unverified").strip().lower()
    if status not in ("unverified", "verified", "rejected"):
        status = "unverified"

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            f"{_ADMIN_PAPER_SELECT} WHERE p.verification_status = %s "
            "ORDER BY p.upload_date DESC",
            (status,),
        )
        rows = cur.fetchall()

    papers = [_paper_to_dict(r) for r in rows]
    return jsonify({"queue": papers, "status": status, "count": len(papers)}), 200


@admin_bp.route("/papers/<int:paper_id>/verify", methods=["POST"])
@admin_required
def verify_paper(paper_id):
    """
    POST /admin/papers/<id>/verify
    Body: { "action": "approve" | "reject", "rejection_note": optional str }
    Sets verification_status and verified_by admin user ID.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    action         = (data.get("action") or "").strip().lower()
    rejection_note = (data.get("rejection_note") or "").strip()

    if action not in ("approve", "reject"):
        return jsonify({"error": "action must be 'approve' or 'reject'"}), 400

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title FROM papers WHERE id = %s", (paper_id,))
        paper = cur.fetchone()
        if not paper:
            return jsonify({"error": f"Paper {paper_id} not found"}), 404

        if action == "approve":
            cur.execute(
                "UPDATE papers SET verification_status = 'verified', verified_by = %s, rejection_note = NULL WHERE id = %s",
                (current_user_id, paper_id),
            )
            message = f"Paper '{paper['title']}' successfully verified and made public!"
        else:
            cur.execute(
                "UPDATE papers SET verification_status = 'rejected', verified_by = %s, rejection_note = %s WHERE id = %s",
                (current_user_id, rejection_note or "Rejected by admin", paper_id),
            )
            message = f"Paper '{paper['title']}' marked as rejected."

        conn.commit()

        cur.execute(f"{_ADMIN_PAPER_SELECT} WHERE p.id = %s", (paper_id,))
        updated_row = cur.fetchone()

        if action == "approve" and updated_row:
            _notify_new_paper(
                conn,
                paper_id,
                updated_row.get("title", paper.get("title")),
                updated_row.get("exam_name", "Exam"),
                updated_row.get("year", 2024),
                updated_row.get("exam_slug", "upsc"),
            )

    return jsonify({"message": message, "paper": _paper_to_dict(updated_row)}), 200


@admin_bp.route("/verification-stats", methods=["GET"])
@verifier_or_admin_required
def get_verification_stats():
    """
    GET /admin/verification-stats
    Returns verification status counts per exam.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                e.id, e.name AS exam_name, e.slug AS exam_slug, e.accent_color_hex,
                SUM(CASE WHEN p.verification_status = 'verified'   THEN 1 ELSE 0 END) AS verified,
                SUM(CASE WHEN p.verification_status = 'unverified' THEN 1 ELSE 0 END) AS unverified,
                SUM(CASE WHEN p.verification_status = 'rejected'   THEN 1 ELSE 0 END) AS rejected
            FROM exams e
            LEFT JOIN exam_categories ec ON ec.exam_id = e.id
            LEFT JOIN papers p ON p.exam_category_id = ec.id
            GROUP BY e.id, e.name, e.slug, e.accent_color_hex
            ORDER BY e.name
            """
        )
        rows = cur.fetchall()

    stats = [
        {
            "exam_name":        r["exam_name"],
            "exam_slug":        r["exam_slug"],
            "accent_color_hex": r["accent_color_hex"],
            "verified":         int(r["verified"] or 0),
            "unverified":       int(r["unverified"] or 0),
            "rejected":         int(r["rejected"] or 0),
            "total":            int((r["verified"] or 0) + (r["unverified"] or 0) + (r["rejected"] or 0)),
        }
        for r in rows
    ]
    return jsonify({"verification_stats": stats}), 200
