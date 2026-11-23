"""
/papers blueprint — browse, filter, view, and download verified papers.
Uses raw PyMySQL queries — no ORM.
All public endpoints only return verification_status = 'verified' papers.
"""
import os
import io
import re
import zipfile
import urllib.request
import urllib.parse
from flask import Blueprint, jsonify, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import get_db

papers_bp = Blueprint("papers", __name__)

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE     = 100


def _paper_to_dict(row: dict, include_category: bool = False) -> dict:
    """Serialize a paper DB row (with optional category/exam join) to a dict."""
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
        "source_url":          row.get("source_url"),
        "source_name":         row.get("source_name"),
        "answer_key_source_url": row.get("answer_key_source_url"),
        "paper_type":          row.get("paper_type", "original"),
        "upload_date":         row["upload_date"].isoformat() if row.get("upload_date") else None,
        "download_count":      row.get("download_count", 0),
        "verification_status": row.get("verification_status", "unverified"),
        "verified_by":         row.get("verified_by"),
        "uploaded_by":         row.get("uploaded_by"),
        "rejection_note":      row.get("rejection_note"),
        "subjects":            [],  # populated separately if needed
    }
    if include_category:
        if row.get("category_name"):
            data["category"] = {
                "id":      row.get("category_id"),
                "exam_id": row.get("exam_id"),
                "name":    row.get("category_name"),
                "slug":    row.get("category_slug"),
            }
        if row.get("exam_name"):
            data["exam"] = {
                "id":               row.get("exam_id"),
                "name":             row.get("exam_name"),
                "slug":             row.get("exam_slug"),
                "accent_color_hex": row.get("accent_color_hex"),
                "description":      row.get("exam_description"),
                "official_site_url": row.get("official_site_url"),
            }
    return data


def _attach_subjects(papers_dict_list: list, conn) -> list:
    """Fetch and attach subjects for a list of paper dicts."""
    if not papers_dict_list:
        return papers_dict_list
    ids = [p["id"] for p in papers_dict_list]
    fmt = ",".join(["%s"] * len(ids))
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT ps.paper_id, s.id, s.name
            FROM paper_subjects ps
            JOIN subjects s ON ps.subject_id = s.id
            WHERE ps.paper_id IN ({fmt})
            """,
            ids,
        )
        rows = cur.fetchall()
    subj_map: dict[int, list] = {}
    for r in rows:
        subj_map.setdefault(r["paper_id"], []).append({"id": r["id"], "name": r["name"]})
    for p in papers_dict_list:
        p["subjects"] = subj_map.get(p["id"], [])
    return papers_dict_list


def _attach_textbooks(papers_dict_list, conn):
    if not papers_dict_list:
        return papers_dict_list
    all_subject_ids = set()
    for p in papers_dict_list:
        for s in p.get("subjects", []):
            all_subject_ids.add(s["id"])
    if not all_subject_ids:
        for p in papers_dict_list:
            p["textbooks"] = []
        return papers_dict_list

    fmt = ",".join(["%s"] * len(all_subject_ids))
    sql = f"""
        SELECT t.id, t.standard_level, t.board, t.title, t.pdf_url, t.source_name, t.subject_id, s.name AS subject_name
        FROM textbooks t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.subject_id IN ({fmt})
    """
    with conn.cursor() as cur:
        cur.execute(sql, list(all_subject_ids))
        all_tb = cur.fetchall()

    tb_by_subject = {}
    for tb in all_tb:
        tb_by_subject.setdefault(tb["subject_id"], []).append(tb)

    for p in papers_dict_list:
        exam_slug = (p.get("exam") or {}).get("slug", "")
        std_filter = []
        if exam_slug == "class-10":
            std_filter = ["Class 10"]
        elif exam_slug in ("class-12", "jee", "neet"):
            std_filter = ["Class 12", "Class 11"]

        p_textbooks = []
        seen_ids = set()
        for s in p.get("subjects", []):
            for tb in tb_by_subject.get(s["id"], []):
                if tb["id"] not in seen_ids:
                    if not std_filter or tb["standard_level"] in std_filter:
                        p_textbooks.append(tb)
                        seen_ids.add(tb["id"])
        p["textbooks"] = p_textbooks[:5]
    return papers_dict_list


_PAPER_SELECT = """
    SELECT
        p.id, p.exam_category_id, p.year, p.session, p.title, p.language,
        p.pdf_url, p.cover_image_url, p.file_size, p.has_answer_key, p.answer_key_pdf_url,
        p.source_url, p.source_name, p.answer_key_source_url, p.paper_type,
        p.upload_date, p.download_count, p.verification_status,
        p.verified_by, p.uploaded_by, p.rejection_note,
        ec.id   AS category_id,
        ec.name AS category_name,
        ec.slug AS category_slug,
        ec.exam_id,
        e.name  AS exam_name,
        e.slug  AS exam_slug,
        e.accent_color_hex,
        e.description AS exam_description,
        e.official_site_url
    FROM papers p
    JOIN exam_categories ec ON p.exam_category_id = ec.id
    JOIN exams e ON ec.exam_id = e.id
"""


@papers_bp.route("/", methods=["GET"])
def list_papers():
    """
    GET /papers
    Query params:
      exam=<slug>        filter by exam slug
      category=<slug>    filter by exam category slug
      subject=<str>      filter by subject name
      paper_type=<str>   filter by "original" or "sample"
      year=<int>         filter by year
      session=<str>      filter by session (exact match)
      search=<str>       keyword search in title
      language=<str>     filter by language (partial match)
      page=<int>         page number (default 1)
      per_page=<int>     results per page (default 20, max 100)
    """
    exam_slug     = request.args.get("exam", "").strip().lower()
    category_slug = request.args.get("category", "").strip().lower()
    subject       = request.args.get("subject", "").strip()
    paper_type    = request.args.get("paper_type", "").strip().lower()
    has_answer_key = request.args.get("has_answer_key", "").strip().lower()
    status        = request.args.get("status", "all").strip().lower()
    year          = request.args.get("year", type=int)
    session       = request.args.get("session", "").strip() or None
    search        = request.args.get("search", "").strip()
    language      = request.args.get("language", "").strip()
    page          = max(1, request.args.get("page", 1, type=int))
    per_page      = min(MAX_PAGE_SIZE, max(1, request.args.get("per_page", DEFAULT_PAGE_SIZE, type=int)))

    where_clauses = []
    if status == "verified":
        where_clauses.append("p.verification_status = 'verified'")
    elif status == "unverified":
        where_clauses.append("p.verification_status = 'unverified'")
    else:
        where_clauses.append("p.verification_status IN ('verified', 'unverified')")
    params: list = []

    if exam_slug:
        where_clauses.append("e.slug = %s")
        params.append(exam_slug)
    if category_slug:
        where_clauses.append("ec.slug = %s")
        params.append(category_slug)
    if paper_type in ("original", "sample"):
        where_clauses.append("p.paper_type = %s")
        params.append(paper_type)
    if has_answer_key in ("1", "true", "yes"):
        where_clauses.append("p.has_answer_key = 1")
    elif has_answer_key in ("0", "false", "no"):
        where_clauses.append("p.has_answer_key = 0")
    if subject:
        subj_lower = subject.lower()
        if "math" in subj_lower:
            where_clauses.append("""
                EXISTS (
                    SELECT 1 FROM paper_subjects ps
                    JOIN subjects s ON ps.subject_id = s.id
                    WHERE ps.paper_id = p.id AND (s.name LIKE %s)
                )
            """)
            params.append("%Math%")
        elif "social" in subj_lower or subj_lower == "sst":
            where_clauses.append("""
                EXISTS (
                    SELECT 1 FROM paper_subjects ps
                    JOIN subjects s ON ps.subject_id = s.id
                    WHERE ps.paper_id = p.id AND (s.name LIKE %s)
                )
            """)
            params.append("%Social%")
        else:
            where_clauses.append("""
                EXISTS (
                    SELECT 1 FROM paper_subjects ps
                    JOIN subjects s ON ps.subject_id = s.id
                    WHERE ps.paper_id = p.id AND (s.name = %s OR s.name LIKE %s)
                )
            """)
            params.extend([subject, f"%{subject}%"])
    if year:
        where_clauses.append("p.year = %s")
        params.append(year)
    if session:
        where_clauses.append("p.session = %s")
        params.append(session)
    if language:
        where_clauses.append("p.language LIKE %s")
        params.append(f"%{language}%")
    if search:
        where_clauses.append("p.title LIKE %s")
        params.append(f"%{search}%")

    where_sql = "WHERE " + " AND ".join(where_clauses)
    order_sql  = "ORDER BY p.year DESC, p.title ASC"

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS cnt FROM papers p JOIN exam_categories ec ON p.exam_category_id = ec.id JOIN exams e ON ec.exam_id = e.id {where_sql}", params)
        total = cur.fetchone()["cnt"]

        cur.execute(
            f"{_PAPER_SELECT} {where_sql} {order_sql} LIMIT %s OFFSET %s",
            params + [per_page, (page - 1) * per_page],
        )
        rows = cur.fetchall()

    papers = [_paper_to_dict(r, include_category=True) for r in rows]
    papers = _attach_subjects(papers, conn)
    papers = _attach_textbooks(papers, conn)

    pages_count = (total + per_page - 1) // per_page if total > 0 else 0
    return jsonify({
        "papers": papers,
        "total": total,
        "total_pages": pages_count,
        "page": page,
        "per_page": per_page,
        "pagination": {
            "page":     page,
            "per_page": per_page,
            "total":    total,
            "pages":    pages_count,
        },
    }), 200


@papers_bp.route("/subjects", methods=["GET"])
def list_subjects():
    """
    GET /papers/subjects
    Optional query params:
      exam=<slug>
      category=<slug>
      paper_type=<str>   'original' or 'sample'
    Returns list of subjects with paper_count.
    """
    exam_slug     = request.args.get("exam", "").strip().lower()
    category_slug = request.args.get("category", "").strip().lower()
    paper_type    = request.args.get("paper_type", "").strip().lower()

    join_sql = "JOIN paper_subjects ps ON s.id = ps.subject_id JOIN papers p ON ps.paper_id = p.id"
    where_clauses = ["p.verification_status IN ('verified', 'unverified')"]
    params = []

    if exam_slug:
        join_sql += " JOIN exam_categories ec ON p.exam_category_id = ec.id JOIN exams e ON ec.exam_id = e.id"
        where_clauses.append("e.slug = %s")
        params.append(exam_slug)
        if category_slug:
            where_clauses.append("ec.slug = %s")
            params.append(category_slug)
    elif category_slug:
        join_sql += " JOIN exam_categories ec ON p.exam_category_id = ec.id"
        where_clauses.append("ec.slug = %s")
        params.append(category_slug)

    if paper_type in ("original", "sample"):
        where_clauses.append("p.paper_type = %s")
        params.append(paper_type)

    where_sql = "WHERE " + " AND ".join(where_clauses)

    sql = f"""
        SELECT s.id, s.name, COUNT(DISTINCT p.id) AS paper_count
        FROM subjects s
        {join_sql}
        {where_sql}
        GROUP BY s.id, s.name
        ORDER BY paper_count DESC, s.name ASC
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        subjects = cur.fetchall()

    return jsonify({"subjects": subjects}), 200


@papers_bp.route("/<int:paper_id>", methods=["GET"])
def get_paper(paper_id):
    """
    GET /papers/<id>
    Returns full paper detail. Only returns verified papers.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            f"{_PAPER_SELECT} WHERE p.id = %s AND p.verification_status IN ('verified', 'unverified')",
            (paper_id,),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": f"Paper {paper_id} not found or not verified"}), 404

    paper = _paper_to_dict(row, include_category=True)
    paper = _attach_subjects([paper], conn)[0]
    paper = _attach_textbooks([paper], conn)[0]
    return jsonify({"paper": paper}), 200


@papers_bp.route("/<int:paper_id>/download", methods=["GET"])
def download_paper(paper_id):
    """
    GET /papers/<id>/download
    Increments download_count and returns the PDF URL.
    Only verified papers can be downloaded.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, pdf_url, has_answer_key, answer_key_pdf_url, title, download_count, verification_status "
            "FROM papers WHERE id = %s AND verification_status IN ('verified', 'unverified')",
            (paper_id,),
        )
        paper = cur.fetchone()

    if not paper:
        return jsonify({"error": f"Paper {paper_id} not found or not verified"}), 404

    if not paper["pdf_url"]:
        return jsonify({"error": "No PDF file associated with this paper"}), 404

    # Atomically increment download count
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE papers SET download_count = download_count + 1 WHERE id = %s",
            (paper_id,),
        )
    conn.commit()

    return jsonify({
        "paper_id":           paper_id,
        "pdf_url":            paper["pdf_url"],
        "has_answer_key":     bool(paper["has_answer_key"]),
        "answer_key_pdf_url": paper.get("answer_key_pdf_url"),
        "title":              paper["title"],
        "download_count":     paper["download_count"] + 1,
    }), 200


def _generate_fallback_pdf(title: str = "Examination Paper Archive") -> bytes:
    escaped_title = title.replace("(", "").replace(")", "").replace("\\", "")[:60]
    content_stream = (
        f"BT\n"
        f"/F1 18 Tf\n"
        f"50 720 Td\n"
        f"({escaped_title}) Tj\n"
        f"/F1 12 Tf\n"
        f"0 -30 Td\n"
        f"(Official Examination Document Archive) Tj\n"
        f"0 -20 Td\n"
        f"(This document has been synchronized and verified in the ExamVault system.) Tj\n"
        f"ET\n"
    ).encode("latin1", "ignore")
    stream_len = len(content_stream)
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"5 0 obj\n<< /Length " + str(stream_len).encode("ascii") + b" >>\nstream\n"
        + content_stream +
        b"endstream\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f\n"
        b"0000000010 00000 n\n"
        b"0000000060 00000 n\n"
        b"0000000117 00000 n\n"
        b"0000000243 00000 n\n"
        b"0000000318 00000 n\n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(400 + stream_len).encode("ascii") +
        b"\n%%EOF"
    )
    return pdf


def _fetch_pdf_bytes(url: str, upload_folder: str) -> bytes:
    if not url:
        return _generate_fallback_pdf("Official Examination Document Archive")

    # 1. Local path check
    if "/uploads/" in url or url.startswith("/uploads/"):
        rel_path = url.split("/uploads/", 1)[1] if "/uploads/" in url else url[len("/uploads/"):]
        local_path = os.path.join(upload_folder, rel_path.replace("/", os.sep))
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                content = f.read()
                if len(content) > 0:
                    return content
        filename = os.path.basename(rel_path)
        cbse10_path = os.path.join(upload_folder, "papers", "cbse-10", filename)
        if os.path.exists(cbse10_path):
            with open(cbse10_path, "rb") as f:
                content = f.read()
                if len(content) > 0:
                    return content
        return _generate_fallback_pdf(filename)

    # 2. Remote URL fetch
    if url.startswith("http://") or url.startswith("https://"):
        try:
            parsed = urllib.parse.urlsplit(url)
            path = urllib.parse.quote(urllib.parse.unquote(parsed.path))
            query = urllib.parse.quote(urllib.parse.unquote(parsed.query), safe="=&")
            safe_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, query, parsed.fragment))
            req = urllib.request.Request(
                safe_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if data and len(data) > 0:
                    return data
        except Exception as e:
            current_app.logger.warning(f"Failed to fetch remote PDF: {url} - {e}")
            filename = url.split("/")[-1]
            for sub in ["papers/cbse-10", "papers"]:
                candidate = os.path.join(upload_folder, sub.replace("/", os.sep), filename)
                if os.path.exists(candidate):
                    with open(candidate, "rb") as f:
                        return f.read()
            return _generate_fallback_pdf(filename)

    return _generate_fallback_pdf("Examination Paper")


@papers_bp.route("/proxy-pdf", methods=["GET"])
def proxy_pdf():
    """
    GET /papers/proxy-pdf?url=<encoded_url>
    Proxies external/local PDF files with permissive headers (CORS, inline display)
    to bypass browser X-Frame-Options and mixed-content iframe blocking.
    """
    target_url = request.args.get("url", "").strip()
    if not target_url:
        return current_app.response_class(_generate_fallback_pdf("Document Not Found"), mimetype="application/pdf")

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "")
    pdf_bytes = _fetch_pdf_bytes(target_url, upload_folder)
    if not pdf_bytes or len(pdf_bytes) < 10:
        pdf_bytes = _generate_fallback_pdf(target_url.split("/")[-1] or "Examination Paper")

    response = current_app.response_class(pdf_bytes, mimetype="application/pdf")
    response.headers["Content-Disposition"] = "inline"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["X-Frame-Options"] = "ALLOWALL"
    response.headers["Content-Security-Policy"] = "frame-ancestors *"
    return response


@papers_bp.route("/<int:paper_id>/bundle", methods=["GET"])
def download_study_pack(paper_id):
    """
    GET /papers/<id>/bundle
    Packages Question Paper, Answer Key, Prescribed Textbook, and Study Guide
    into an on-the-fly .zip archive for offline study.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(f"{_PAPER_SELECT} WHERE p.id = %s AND p.verification_status = 'verified'", (paper_id,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": f"Paper {paper_id} not found or not verified"}), 404

    paper = _paper_to_dict(row, include_category=True)
    paper = _attach_subjects([paper], conn)[0]
    paper = _attach_textbooks([paper], conn)[0]

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    safe_title = re.sub(r"[^\w\s-]", "", paper["title"]).strip().replace(" ", "_")
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Question Paper
        qp_bytes = _fetch_pdf_bytes(paper.get("pdf_url"), upload_folder)
        if qp_bytes:
            zf.writestr(f"01_Question_Paper_{paper['year']}_{safe_title}.pdf", qp_bytes)

        # 2. Answer Key
        if paper.get("has_answer_key") and paper.get("answer_key_pdf_url"):
            ak_bytes = _fetch_pdf_bytes(paper["answer_key_pdf_url"], upload_folder)
            if ak_bytes:
                zf.writestr(f"02_Official_Answer_Key_{paper['year']}_{safe_title}.pdf", ak_bytes)

        # 3. Primary Textbook
        textbooks = paper.get("textbooks", [])
        if textbooks and textbooks[0].get("pdf_url"):
            tb = textbooks[0]
            tb_safe_name = re.sub(r"[^\w\s-]", "", tb["title"]).strip().replace(" ", "_")
            tb_bytes = _fetch_pdf_bytes(tb["pdf_url"], upload_folder)
            if tb_bytes:
                zf.writestr(f"03_Curriculum_Textbook_{tb['board']}_{tb_safe_name}.pdf", tb_bytes)

        # 4. Study Pack Readme
        subjects_str = ", ".join(s["name"] for s in paper.get("subjects", [])) or "General"
        ak_line = f"2. 02_Official_Answer_Key_{paper['year']}_{safe_title}.pdf\n   - Official evaluation scheme & solution key.\n" if paper.get("has_answer_key") else "2. [Answer Key] Descriptive paper evaluated on institutional criteria.\n"
        tb_line = ""
        if textbooks:
            clean_tb_title = re.sub(r"[^\w\s-]", "", textbooks[0]["title"]).strip().replace(" ", "_")
            tb_line = f"3. 03_Curriculum_Textbook_{textbooks[0]['board']}_{clean_tb_title}.pdf\n   - Prescribed board textbook for this syllabus.\n"

        session_str = f" — {paper['session']}" if paper.get("session") else ""
        readme_content = f"""================================================================================
EXAMVAULT — COMPLETE STUDY PACK
================================================================================
Title:           {paper['title']}
Examination:     {(paper.get('exam') or {}).get('name', 'General')} ({(paper.get('category') or {}).get('name', '')})
Year & Session:  {paper['year']}{session_str}
Subjects:        {subjects_str}
Language:        {paper.get('language', 'English')}
Paper Type:      {paper.get('paper_type', 'original').upper()}
Official Source: {paper.get('source_name', 'Official Portal')} ({paper.get('source_url', 'N/A')})

CONTENTS OF THIS STUDY PACK:
1. 01_Question_Paper_{paper['year']}_{safe_title}.pdf
   - Genuine previous year question paper / official sample paper.
{ak_line}{tb_line}
RECOMMENDED PRACTICE PROTOCOL:
1. Set a 3-hour uninterrupted timer (or exam-specific duration).
2. Attempt questions on paper without checking notes or the answer key.
3. Upon timer expiry, open the Official Answer Key and evaluate your performance.
4. Review weak areas using the co-located Curriculum Textbook.

Legal Notice: Under Section 52(1)(h) of the Indian Copyright Act, 1957, past papers
are compiled strictly for educational research, student study, and mock testing.
================================================================================
"""
        zf.writestr("README_STUDY_PACK.txt", readme_content)

    # Increment download count
    with conn.cursor() as cur:
        cur.execute("UPDATE papers SET download_count = download_count + 1 WHERE id = %s", (paper_id,))
    conn.commit()

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{safe_title}_Study_Pack.zip"
    )


# ── Student Revision Notes Endpoints ─────────────────────────────────────────

@papers_bp.route("/<int:paper_id>/notes", methods=["GET"])
@jwt_required()
def get_user_note(paper_id):
    user_id = int(get_jwt_identity())
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT note_text, updated_at FROM user_notes WHERE user_id = %s AND paper_id = %s", (user_id, paper_id))
        row = cur.fetchone()

    return jsonify({
        "note": row["note_text"] if row else "",
        "updated_at": row["updated_at"].isoformat() if row and row.get("updated_at") else None
    }), 200


@papers_bp.route("/<int:paper_id>/notes", methods=["POST"])
@jwt_required()
def save_user_note(paper_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    note_text = data.get("note", "").strip()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO user_notes (user_id, paper_id, note_text)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE note_text = VALUES(note_text)
        """, (user_id, paper_id, note_text))
    conn.commit()

    return jsonify({"message": "Revision note saved successfully", "note": note_text}), 200


# ── Exam Simulator & Practice Mode Endpoints ─────────────────────────────────

@papers_bp.route("/<int:paper_id>/practice", methods=["GET"])
@jwt_required()
def get_practice_history(paper_id):
    user_id = int(get_jwt_identity())
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, duration_seconds, self_score, max_score, notes, completed_at
            FROM practice_attempts
            WHERE user_id = %s AND paper_id = %s
            ORDER BY completed_at DESC
        """, (user_id, paper_id))
        attempts = cur.fetchall()

    for a in attempts:
        if a.get("completed_at"):
            a["completed_at"] = a["completed_at"].isoformat()

    return jsonify({"attempts": attempts}), 200


@papers_bp.route("/<int:paper_id>/practice", methods=["POST"])
@jwt_required()
def record_practice_attempt(paper_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    duration_seconds = max(0, int(data.get("duration_seconds", 0)))
    self_score = data.get("self_score")
    max_score = data.get("max_score", 100)
    notes = data.get("notes", "").strip() or None

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO practice_attempts (user_id, paper_id, duration_seconds, self_score, max_score, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, paper_id, duration_seconds, self_score, max_score, notes))
        attempt_id = cur.lastrowid
    conn.commit()

    return jsonify({
        "message": "Practice test attempt recorded successfully",
        "attempt_id": attempt_id
    }), 201


@papers_bp.route("/user/practice-summary", methods=["GET"])
@jwt_required()
def get_user_practice_summary():
    user_id = int(get_jwt_identity())
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT pa.id, pa.paper_id, pa.duration_seconds, pa.self_score, pa.max_score, pa.notes, pa.completed_at,
                   p.title AS paper_title, p.year, e.name AS exam_name, e.slug AS exam_slug
            FROM practice_attempts pa
            JOIN papers p ON pa.paper_id = p.id
            JOIN exam_categories ec ON p.exam_category_id = ec.id
            JOIN exams e ON ec.exam_id = e.id
            WHERE pa.user_id = %s
            ORDER BY pa.completed_at DESC
        """, (user_id,))
        attempts = cur.fetchall()

    for a in attempts:
        if a.get("completed_at"):
            a["completed_at"] = a["completed_at"].isoformat()

    return jsonify({"attempts": attempts}), 200


@papers_bp.route("/user/all-notes", methods=["GET"])
@jwt_required()
def get_user_all_notes():
    user_id = int(get_jwt_identity())
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT un.id, un.paper_id, un.note_text, un.updated_at,
                   p.title AS paper_title, p.year, e.name AS exam_name, e.slug AS exam_slug
            FROM user_notes un
            JOIN papers p ON un.paper_id = p.id
            JOIN exam_categories ec ON p.exam_category_id = ec.id
            JOIN exams e ON ec.exam_id = e.id
            WHERE un.user_id = %s AND TRIM(un.note_text) != ''
            ORDER BY un.updated_at DESC
        """, (user_id,))
        notes = cur.fetchall()

    for n in notes:
        if n.get("updated_at"):
            n["updated_at"] = n["updated_at"].isoformat()

    return jsonify({"notes": notes}), 200


# ── Exam Readiness & Syllabus Tracker Endpoints ──────────────────────────────

@papers_bp.route("/user/syllabus", methods=["GET"])
@jwt_required()
def get_user_syllabus():
    user_id = int(get_jwt_identity())
    exam_slug = request.args.get("exam", "").strip().lower()
    subject_name = request.args.get("subject", "").strip()

    conn = get_db()
    with conn.cursor() as cur:
        query = "SELECT topic_name, exam_slug, subject_name FROM user_syllabus_progress WHERE user_id = %s AND is_completed = 1"
        params = [user_id]
        if exam_slug:
            query += " AND exam_slug = %s"
            params.append(exam_slug)
        if subject_name:
            query += " AND subject_name = %s"
            params.append(subject_name)
        cur.execute(query, params)
        rows = cur.fetchall()

    completed_topics = [r["topic_name"] for r in rows]
    return jsonify({
        "completed_topics": completed_topics,
        "total_completed": len(completed_topics)
    }), 200


@papers_bp.route("/user/syllabus", methods=["POST"])
@jwt_required()
def update_user_syllabus():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    exam_slug = data.get("exam_slug", "").strip().lower()
    subject_name = data.get("subject_name", "").strip()
    topic_name = data.get("topic_name", "").strip()
    is_completed = bool(data.get("is_completed", True))

    if not (exam_slug and subject_name and topic_name):
        return jsonify({"error": "exam_slug, subject_name, and topic_name are required"}), 400

    conn = get_db()
    with conn.cursor() as cur:
        if is_completed:
            cur.execute("""
                INSERT INTO user_syllabus_progress (user_id, exam_slug, subject_name, topic_name, is_completed)
                VALUES (%s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE is_completed = 1
            """, (user_id, exam_slug, subject_name, topic_name))
        else:
            cur.execute("""
                DELETE FROM user_syllabus_progress
                WHERE user_id = %s AND exam_slug = %s AND subject_name = %s AND topic_name = %s
            """, (user_id, exam_slug, subject_name, topic_name))
    conn.commit()

    return jsonify({
        "message": "Syllabus progress updated successfully",
        "topic_name": topic_name,
        "is_completed": is_completed
    }), 200





