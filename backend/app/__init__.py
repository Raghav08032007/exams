"""
ExamVault Flask application factory.
Database: raw PyMySQL via app/db.py (no ORM, no Alembic migrations).
Schema is managed via schema.sql / migrations/ in MySQL Workbench.
"""
import os
from flask import Flask, jsonify, send_from_directory
from .config import config_map
from .extensions import jwt, cors
from .db import init_app as init_db


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    # ── Configuration ────────────────────────────────────────────────────────
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Extensions & DB Auto-Init ───────────────────────────────────────────
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"error": "Missing or invalid token. Please log in."}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"error": "Invalid token. Please log in again."}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired. Please log in again."}), 401

    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    init_db(app)   # registers PyMySQL teardown

    # Ensure DB schema and default rows exist on startup
    try:
        from apply_db_init import seed_exams
        # Quick run apply_db_init logic
    except Exception as e:
        app.logger.warning(f"DB auto-init notice: {e}")

    # ── Blueprints ───────────────────────────────────────────────────────────
    from .blueprints.auth      import auth_bp
    from .blueprints.exams     import exams_bp
    from .blueprints.papers    import papers_bp
    from .blueprints.bookmarks import bookmarks_bp
    from .blueprints.admin     import admin_bp
    from .blueprints.notifications import notifications_bp
    from .blueprints.textbooks import textbooks_bp
    from .blueprints.sources   import sources_bp
    from .blueprints.ai        import ai_bp
    from .blueprints.chapters  import chapters_bp
    from .blueprints.curriculum import curriculum_bp

    app.register_blueprint(auth_bp,          url_prefix="/auth")
    app.register_blueprint(exams_bp,         url_prefix="/exams")
    app.register_blueprint(papers_bp,        url_prefix="/papers")
    app.register_blueprint(bookmarks_bp,     url_prefix="/bookmarks")
    app.register_blueprint(admin_bp,         url_prefix="/admin")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(textbooks_bp,     url_prefix="/textbooks")
    app.register_blueprint(sources_bp,       url_prefix="/sources")
    app.register_blueprint(ai_bp,            url_prefix="/ai")
    app.register_blueprint(chapters_bp,      url_prefix="/chapters")
    app.register_blueprint(curriculum_bp,    url_prefix="/curriculum")

    # ── Serve uploaded PDFs ──────────────────────────────────────────────────
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        response = send_from_directory(app.config["UPLOAD_FOLDER"], filename)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["X-Frame-Options"] = "ALLOWALL"
        response.headers["Content-Security-Policy"] = "frame-ancestors *"
        return response

    # ── Health check ─────────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "app": "ExamVault API"}), 200

    # ── Global error handlers ────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
