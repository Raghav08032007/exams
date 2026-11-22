"""
/exams blueprint — browse exams, categories, and year+session listings.
Uses raw PyMySQL queries — no ORM.
"""
from flask import Blueprint, jsonify, request
from ..db import get_db

exams_bp = Blueprint("exams", __name__)


def _exam_to_dict(row: dict, categories: list | None = None) -> dict:
    data = {
        "id":               row["id"],
        "name":             row["name"],
        "slug":             row["slug"],
        "description":      row["description"],
        "accent_color_hex": row["accent_color_hex"],
        "official_site_url": row.get("official_site_url"),
    }
    if categories is not None:
        data["categories"] = categories
    return data


def _category_to_dict(row: dict) -> dict:
    return {
        "id":      row["id"],
        "exam_id": row["exam_id"],
        "name":    row["name"],
        "slug":    row["slug"],
    }


@exams_bp.route("/", methods=["GET"])
def list_exams():
    """
    GET /exams
    Returns all exams with accent colors, descriptions, and official_site_url.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, slug, description, accent_color_hex, official_site_url "
            "FROM exams ORDER BY name"
        )
        exams = cur.fetchall()
    return jsonify({"exams": [_exam_to_dict(e) for e in exams]}), 200


@exams_bp.route("/<string:slug>", methods=["GET"])
def get_exam(slug):
    """
    GET /exams/<slug>
    Returns a single exam with its categories and official_site_url.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, slug, description, accent_color_hex, official_site_url "
            "FROM exams WHERE slug = %s",
            (slug,),
        )
        exam = cur.fetchone()
        if not exam:
            return jsonify({"error": f"Exam '{slug}' not found"}), 404

        cur.execute(
            "SELECT id, exam_id, name, slug FROM exam_categories "
            "WHERE exam_id = %s ORDER BY name",
            (exam["id"],),
        )
        categories = [_category_to_dict(c) for c in cur.fetchall()]

    return jsonify({"exam": _exam_to_dict(exam, categories=categories)}), 200


@exams_bp.route("/<string:slug>/categories", methods=["GET"])
def get_categories(slug):
    """
    GET /exams/<slug>/categories
    Returns all categories for a given exam.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM exams WHERE slug = %s", (slug,))
        exam = cur.fetchone()
        if not exam:
            return jsonify({"error": f"Exam '{slug}' not found"}), 404

        cur.execute(
            "SELECT id, exam_id, name, slug FROM exam_categories "
            "WHERE exam_id = %s ORDER BY name",
            (exam["id"],),
        )
        categories = [_category_to_dict(c) for c in cur.fetchall()]

    return jsonify({"exam_slug": slug, "categories": categories}), 200


@exams_bp.route("/<string:slug>/categories/<string:cat_slug>/year-sessions", methods=["GET"])
def get_year_sessions(slug, cat_slug):
    """
    GET /exams/<slug>/categories/<cat_slug>/year-sessions
    Returns distinct {year, session} pairs for verified papers in this category.
    Sorted by year DESC, session ASC (NULL sessions first).
    Used by the Category page to render year+session cards.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM exams WHERE slug = %s", (slug,))
        exam = cur.fetchone()
        if not exam:
            return jsonify({"error": f"Exam '{slug}' not found"}), 404

        cur.execute(
            "SELECT id FROM exam_categories WHERE exam_id = %s AND slug = %s",
            (exam["id"], cat_slug),
        )
        category = cur.fetchone()
        if not category:
            return jsonify({"error": f"Category '{cat_slug}' not found"}), 404

        cur.execute(
            """
            SELECT DISTINCT year, session
            FROM papers
            WHERE exam_category_id = %s
              AND verification_status = 'verified'
            ORDER BY year DESC, session ASC
            """,
            (category["id"],),
        )
        rows = cur.fetchall()

    # Normalize None → null, ensure JSON-safe types
    year_sessions = [
        {"year": int(r["year"]), "session": r["session"]}
        for r in rows
    ]
    return jsonify({
        "exam_slug":    slug,
        "category_slug": cat_slug,
        "year_sessions": year_sessions,
    }), 200


@exams_bp.route("/<string:slug>/years", methods=["GET"])
def get_years(slug):
    """
    GET /exams/<slug>/years
    Legacy endpoint — returns distinct years across all categories (or filtered by ?category=).
    Kept for backward compatibility with search page.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM exams WHERE slug = %s", (slug,))
        exam = cur.fetchone()
        if not exam:
            return jsonify({"error": f"Exam '{slug}' not found"}), 404

        category_slug = request.args.get("category")

        if category_slug:
            cur.execute(
                """
                SELECT DISTINCT p.year
                FROM papers p
                JOIN exam_categories ec ON p.exam_category_id = ec.id
                WHERE ec.exam_id = %s
                  AND ec.slug = %s
                  AND p.verification_status = 'verified'
                ORDER BY p.year DESC
                """,
                (exam["id"], category_slug),
            )
        else:
            cur.execute(
                """
                SELECT DISTINCT p.year
                FROM papers p
                JOIN exam_categories ec ON p.exam_category_id = ec.id
                WHERE ec.exam_id = %s
                  AND p.verification_status = 'verified'
                ORDER BY p.year DESC
                """,
                (exam["id"],),
            )
        years = [row["year"] for row in cur.fetchall()]

    return jsonify({"exam_slug": slug, "years": years}), 200
