"""
Sources and Open Archive Provenance Blueprint.
Documents all GitHub repositories, official examination portals, mirror CDNs,
and resource metrics indexed in ExamVault with live database counts and verification classification.
"""
from flask import Blueprint, jsonify, request
from ..db import get_db

sources_bp = Blueprint("sources", __name__)


@sources_bp.route("/", methods=["GET"])
def get_sources():
    category_filter = request.args.get("category", "").strip()
    search_query = request.args.get("search", "").strip()

    conn = get_db()
    with conn.cursor() as cur:
        # Total counts
        cur.execute("SELECT COUNT(*) AS cnt FROM papers")
        total_papers = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM papers WHERE verification_status = 'verified'")
        verified_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM papers WHERE verification_status = 'unverified'")
        unverified_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM papers WHERE has_answer_key = 1")
        keys_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM textbooks")
        textbooks_count = cur.fetchone()["cnt"]

        # Filtered sources query from database
        sql = "SELECT id, name, category, source_type, url, direct_repo_path, description, papers_count, status FROM sources"
        where = []
        params = []
        if category_filter:
            where.append("category = %s")
            params.append(category_filter)
        if search_query:
            where.append("(name LIKE %s OR description LIKE %s)")
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY papers_count DESC, name ASC"

        cur.execute(sql, params)
        all_sources = cur.fetchall()

        # Counts by source name
        cur.execute("""
            SELECT COALESCE(source_name, 'Official Portal') AS source_name, COUNT(*) AS count
            FROM papers
            GROUP BY source_name
            ORDER BY count DESC
        """)
        paper_sources = cur.fetchall()

    return jsonify({
        "metrics": {
            "total_papers": total_papers,
            "verified_papers": verified_count,
            "unverified_papers": unverified_count,
            "answer_keys": keys_count,
            "textbooks": textbooks_count,
        },
        "sources": all_sources,
        "paper_sources": paper_sources,
    }), 200
