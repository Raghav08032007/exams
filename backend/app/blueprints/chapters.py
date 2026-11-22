"""
Chapters & Lessons Blueprint — Subject-to-Lesson / Chapter Explorer.
Co-locates textbook chapter content with curated questions from Oswaal Books,
NCERT Exemplar, Arihant, and Board PYQs.
"""
from flask import Blueprint, jsonify, request, current_app
from ..db import get_db

chapters_bp = Blueprint("chapters", __name__)


@chapters_bp.route("/", methods=["GET"])
def list_chapters():
    """
    GET /chapters/
    Query parameters:
    - exam: exam slug (class-10, class-12, jee, neet, upsc, tnpsc)
    - standard: standard level (Class 10, Class 12, etc.)
    - subject: subject name or ID
    """
    exam_slug = request.args.get("exam", "").strip().lower()
    standard = request.args.get("standard", "").strip()
    subject = request.args.get("subject", "").strip()
    education = request.args.get("education", "").strip().lower()
    domain = request.args.get("domain", "").strip().lower()
    search = request.args.get("q", "").strip().lower()

    where_clauses = []
    params = []

    if exam_slug:
        where_clauses.append("c.exam_slug = %s")
        params.append(exam_slug)
    if standard:
        where_clauses.append("c.standard_level = %s")
        params.append(standard)
    if subject:
        if subject.isdigit():
            where_clauses.append("c.subject_id = %s")
            params.append(int(subject))
        else:
            where_clauses.append("LOWER(s.name) = %s")
            params.append(subject.lower())

    if education == "school":
        where_clauses.append("c.standard_level IN ('Class 10', 'Class 12')")
    elif education == "entrance":
        where_clauses.append("c.standard_level IN ('JEE', 'NEET')")
    elif education == "civil_services":
        where_clauses.append("c.standard_level IN ('UPSC', 'TNPSC')")
    elif education == "defence":
        where_clauses.append("c.standard_level IN ('NDA', 'CDS', 'Defence')")

    if domain == "math":
        where_clauses.append("s.name IN ('Mathematics', 'Algebra', 'Geometry', 'Trigonometry', 'Calculus', 'Statistics', 'Aptitude')")
    elif domain == "science":
        where_clauses.append("s.name IN ('Science', 'Physics', 'Chemistry', 'Biology', 'Botany', 'Zoology')")
    elif domain == "social":
        where_clauses.append("s.name IN ('Social Science', 'History', 'Geography', 'Polity', 'Civics', 'Economics')")
    elif domain == "languages":
        where_clauses.append("s.name IN ('English', 'Tamil', 'General Tamil', 'Hindi', 'Sanskrit', 'Arabic')")
    elif domain == "tech_commerce":
        where_clauses.append("s.name IN ('Information Technology', 'Computer Science', 'Accountancy', 'Business Studies')")
    elif domain == "general_studies":
        where_clauses.append("s.name IN ('General Studies', 'CSAT', 'Current Affairs', 'Mental Ability', 'General Knowledge')")

    if search:
        where_clauses.append("(LOWER(c.chapter_title) LIKE %s OR LOWER(c.summary_notes) LIKE %s OR LOWER(s.name) LIKE %s)")
        search_wild = f"%{search}%"
        params.extend([search_wild, search_wild, search_wild])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT c.id, c.exam_slug, c.standard_level, c.board,
               c.chapter_number, c.chapter_title, c.summary_notes,
               c.marks_weightage, c.textbook_chapter_url,
               s.id AS subject_id, s.name AS subject_name,
               COUNT(cq.id) AS question_count
        FROM chapters c
        JOIN subjects s ON c.subject_id = s.id
        LEFT JOIN chapter_questions cq ON c.id = cq.chapter_id
        {where_sql}
        GROUP BY c.id, s.id
        ORDER BY c.chapter_number ASC, c.chapter_title ASC
    """

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        chapters = cur.fetchall()

    return jsonify({
        "chapters": chapters,
        "total": len(chapters)
    }), 200


@chapters_bp.route("/<int:chapter_id>", methods=["GET"])
def get_chapter(chapter_id):
    """
    GET /chapters/<id>
    Returns full chapter metadata, textbook reading stream, and all lesson questions.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.exam_slug, c.standard_level, c.board,
                   c.chapter_number, c.chapter_title, c.summary_notes,
                   c.marks_weightage, c.textbook_chapter_url,
                   s.id AS subject_id, s.name AS subject_name
            FROM chapters c
            JOIN subjects s ON c.subject_id = s.id
            WHERE c.id = %s
        """, (chapter_id,))
        chapter = cur.fetchone()

        if not chapter:
            return jsonify({"error": f"Chapter {chapter_id} not found"}), 404

        cur.execute("""
            SELECT id, question_text, question_type, marks,
                   answer_explanation, source_publication, difficulty, year
            FROM chapter_questions
            WHERE chapter_id = %s
            ORDER BY marks ASC, id ASC
        """, (chapter_id,))
        questions = cur.fetchall()

    chapter["questions"] = questions
    chapter["question_count"] = len(questions)

    # Provide streaming proxy URL for chapter textbook PDF
    if chapter.get("textbook_chapter_url"):
        import urllib.parse
        encoded_url = urllib.parse.quote(chapter["textbook_chapter_url"])
        chapter["proxied_textbook_url"] = f"/papers/proxy-pdf?url={encoded_url}"
    else:
        chapter["proxied_textbook_url"] = None

    return jsonify({"chapter": chapter}), 200
