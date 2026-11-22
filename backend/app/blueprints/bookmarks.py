"""
/bookmarks blueprint — save and retrieve a user's bookmarked papers.
All routes require a valid JWT.
Uses raw PyMySQL queries — no ORM.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import get_db

bookmarks_bp = Blueprint("bookmarks", __name__)


def _bookmark_to_dict(row: dict) -> dict:
    data = {
        "id":         row["id"],
        "user_id":    row["user_id"],
        "paper_id":   row["paper_id"],
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }
    # Include paper info if available (from join)
    if row.get("paper_title"):
        data["paper"] = {
            "id":               row["paper_id"],
            "title":            row.get("paper_title"),
            "year":             row.get("paper_year"),
            "session":          row.get("paper_session"),
            "language":         row.get("paper_language"),
            "has_answer_key":   bool(row.get("has_answer_key", False)),
            "download_count":   row.get("download_count", 0),
            "pdf_url":          row.get("pdf_url"),
            "exam_category_id": row.get("exam_category_id"),
        }
    return data


@bookmarks_bp.route("/", methods=["GET"])
@jwt_required()
def list_bookmarks():
    """
    GET /bookmarks
    Returns all papers bookmarked by the authenticated user, newest first.
    """
    user_id = get_jwt_identity()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                b.id, b.user_id, b.paper_id, b.created_at,
                p.title AS paper_title, p.year AS paper_year,
                p.session AS paper_session, p.language AS paper_language,
                p.has_answer_key, p.download_count, p.pdf_url,
                p.exam_category_id
            FROM bookmarks b
            JOIN papers p ON b.paper_id = p.id
            WHERE b.user_id = %s
            ORDER BY b.created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    return jsonify({"bookmarks": [_bookmark_to_dict(r) for r in rows]}), 200


@bookmarks_bp.route("/", methods=["POST"])
@jwt_required()
def add_bookmark():
    """
    POST /bookmarks
    Body: { "paper_id": int }
    Returns: { "bookmark": {...} }
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)
    if not data or "paper_id" not in data:
        return jsonify({"error": "paper_id is required"}), 400

    paper_id = data["paper_id"]
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM papers WHERE id = %s", (paper_id,))
        if not cur.fetchone():
            return jsonify({"error": f"Paper {paper_id} not found"}), 404

        # Check if already bookmarked
        cur.execute(
            "SELECT id FROM bookmarks WHERE user_id = %s AND paper_id = %s",
            (user_id, paper_id),
        )
        existing = cur.fetchone()
        if existing:
            return jsonify({"message": "Already bookmarked", "bookmark": {"id": existing["id"], "user_id": user_id, "paper_id": paper_id}}), 200

        cur.execute(
            "INSERT INTO bookmarks (user_id, paper_id) VALUES (%s, %s)",
            (user_id, paper_id),
        )
        bookmark_id = cur.lastrowid
        conn.commit()

    return jsonify({"message": "Bookmarked successfully", "bookmark": {"id": bookmark_id, "user_id": user_id, "paper_id": paper_id}}), 201


@bookmarks_bp.route("/<int:bookmark_id>", methods=["DELETE"])
@jwt_required()
def delete_bookmark(bookmark_id):
    """
    DELETE /bookmarks/<id>
    Removes a bookmark. Users can only delete their own bookmarks.
    """
    user_id = get_jwt_identity()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, user_id FROM bookmarks WHERE id = %s", (bookmark_id,))
        bookmark = cur.fetchone()
        if not bookmark:
            return jsonify({"error": "Bookmark not found"}), 404
        if bookmark["user_id"] != user_id:
            return jsonify({"error": "You do not own this bookmark"}), 403
        cur.execute("DELETE FROM bookmarks WHERE id = %s", (bookmark_id,))
        conn.commit()

    return jsonify({"message": "Bookmark removed"}), 200


@bookmarks_bp.route("/paper/<int:paper_id>", methods=["DELETE"])
@jwt_required()
def remove_bookmark_by_paper(paper_id):
    """
    DELETE /bookmarks/paper/<paper_id>
    Convenience: remove bookmark by paper ID.
    """
    user_id = get_jwt_identity()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM bookmarks WHERE user_id = %s AND paper_id = %s",
            (user_id, paper_id),
        )
        bookmark = cur.fetchone()
        if not bookmark:
            return jsonify({"error": "Bookmark not found"}), 404
        cur.execute("DELETE FROM bookmarks WHERE id = %s", (bookmark["id"],))
        conn.commit()

    return jsonify({"message": "Bookmark removed"}), 200
