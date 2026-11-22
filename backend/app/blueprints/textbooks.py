"""
/textbooks blueprint — browse, filter, view, and download standard curriculum textbooks.
Uses raw PyMySQL queries — no ORM.
"""
from flask import Blueprint, jsonify, request
from ..db import get_db

textbooks_bp = Blueprint("textbooks", __name__)

DEFAULT_PAGE_SIZE = 24
MAX_PAGE_SIZE     = 100


def _textbook_to_dict(row: dict) -> dict:
    return {
        "id":             row["id"],
        "standard_level": row["standard_level"],
        "board":          row["board"],
        "subject_id":     row["subject_id"],
        "subject_name":   row.get("subject_name"),
        "title":          row["title"],
        "edition_year":   row.get("edition_year"),
        "language":       row.get("language", "English"),
        "pdf_url":        row.get("pdf_url"),
        "cover_image_url":row.get("cover_image_url"),
        "chapter_number": row.get("chapter_number"),
        "chapter_title":  row.get("chapter_title"),
        "source_url":     row.get("source_url"),
        "source_name":    row.get("source_name"),
        "download_count": row.get("download_count", 0),
        "created_at":     row["created_at"].isoformat() if row.get("created_at") else None,
    }


_TEXTBOOK_SELECT = """
    SELECT
        t.id, t.standard_level, t.board, t.subject_id, t.title,
        t.edition_year, t.language, t.pdf_url, t.cover_image_url,
        t.chapter_number, t.chapter_title, t.source_url, t.source_name,
        t.download_count, t.created_at,
        s.name AS subject_name
    FROM textbooks t
    JOIN subjects s ON t.subject_id = s.id
"""


@textbooks_bp.route("/", methods=["GET"])
def list_textbooks():
    """
    GET /textbooks
    Query params:
      standard=<str>    e.g. "Class 10", "Class 12"
      board=<str>       e.g. "CBSE / NCERT", "Tamil Nadu State Board"
      subject=<str>     subject name
      search=<str>      keyword search in title
      language=<str>    language filter
      page=<int>        page number (default 1)
      per_page=<int>    results per page (default 24)
    """
    standard = request.args.get("standard", "").strip()
    board    = request.args.get("board", "").strip()
    subject  = request.args.get("subject", "").strip()
    search   = request.args.get("search", "").strip()
    language = request.args.get("language", "").strip()
    page     = max(1, request.args.get("page", 1, type=int))
    per_page = min(MAX_PAGE_SIZE, max(1, request.args.get("per_page", DEFAULT_PAGE_SIZE, type=int)))

    where_clauses = ["1=1"]
    params: list = []

    if standard:
        where_clauses.append("(t.standard_level = %s OR t.standard_level LIKE %s)")
        params.extend([standard, f"%{standard}%"])
    if board:
        where_clauses.append("t.board LIKE %s")
        params.append(f"%{board}%")
    if subject:
        where_clauses.append("(s.name = %s OR s.name LIKE %s)")
        params.extend([subject, f"%{subject}%"])
    if language:
        where_clauses.append("t.language LIKE %s")
        params.append(f"%{language}%")
    if search:
        where_clauses.append("(t.title LIKE %s OR s.name LIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_sql = "WHERE " + " AND ".join(where_clauses)
    order_sql = "ORDER BY t.standard_level ASC, s.name ASC, t.title ASC"

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS cnt FROM textbooks t JOIN subjects s ON t.subject_id = s.id {where_sql}", params)
        total = cur.fetchone()["cnt"]

        cur.execute(
            f"{_TEXTBOOK_SELECT} {where_sql} {order_sql} LIMIT %s OFFSET %s",
            params + [per_page, (page - 1) * per_page],
        )
        rows = cur.fetchall()

    textbooks = [_textbook_to_dict(r) for r in rows]

    return jsonify({
        "textbooks": textbooks,
        "pagination": {
            "page":     page,
            "per_page": per_page,
            "total":    total,
            "pages":    (total + per_page - 1) // per_page if total > 0 else 0,
        },
    }), 200


@textbooks_bp.route("/standards", methods=["GET"])
def list_standards():
    """
    GET /textbooks/standards
    Returns grouped list of available standards, boards, and subjects.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT standard_level, board, COUNT(*) as book_count
            FROM textbooks
            GROUP BY standard_level, board
            ORDER BY standard_level ASC, board ASC
        """)
        groups = cur.fetchall()

        cur.execute("""
            SELECT DISTINCT s.name AS subject_name, COUNT(DISTINCT t.id) as book_count
            FROM textbooks t
            JOIN subjects s ON t.subject_id = s.id
            GROUP BY s.name
            ORDER BY book_count DESC
        """)
        subjects = cur.fetchall()

    return jsonify({
        "standards": groups,
        "subjects":  subjects,
    }), 200


@textbooks_bp.route("/<int:textbook_id>", methods=["GET"])
def get_textbook(textbook_id):
    """
    GET /textbooks/<id>
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(f"{_TEXTBOOK_SELECT} WHERE t.id = %s", (textbook_id,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": f"Textbook {textbook_id} not found"}), 404

    return jsonify({"textbook": _textbook_to_dict(row)}), 200
