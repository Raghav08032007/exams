"""
PyMySQL database connection helper.
Provides get_db() (per-request connection via Flask's g) and close_db() teardown.
All queries use parameterized SQL — no ORM, no string interpolation.
"""
import pymysql
import pymysql.cursors
from urllib.parse import urlparse
from flask import g


def _parse_url(database_url: str) -> dict:
    """
    Parse a DATABASE_URL string into PyMySQL connection kwargs.
    Supports:  mysql+pymysql://user:pass@host:port/dbname
               mysql://user:pass@host:port/dbname
    """
    url = database_url.strip()
    # Remove the SQLAlchemy dialect prefix if present
    for prefix in ("mysql+pymysql://", "mysql://", "pymysql://"):
        if url.startswith(prefix):
            url = "mysql://" + url[len(prefix):]
            break
    parsed = urlparse(url)
    return {
        "host":     parsed.hostname or "localhost",
        "port":     parsed.port or 3306,
        "user":     parsed.username or "root",
        "password": parsed.password or "",
        "database": parsed.path.lstrip("/"),
    }


_SCHEMA_CHECKED = False


def _ensure_schema(conn):
    """Run once per app lifecycle to self-heal schema columns and seed data."""
    global _SCHEMA_CHECKED
    if _SCHEMA_CHECKED:
        return
    
    statements = [
        "ALTER TABLE users MODIFY COLUMN role ENUM('user', 'admin', 'verifier') NOT NULL DEFAULT 'user'",
        "ALTER TABLE exams ADD COLUMN official_site_url VARCHAR(255) NULL",
        "ALTER TABLE papers ADD COLUMN session VARCHAR(50) NULL AFTER year",
        "ALTER TABLE papers ADD COLUMN uploaded_by INT NULL AFTER verified_by",
        "ALTER TABLE papers ADD COLUMN cover_image_url VARCHAR(500) NULL AFTER pdf_url",
        "UPDATE exams SET official_site_url = 'https://www.tnpsc.gov.in' WHERE slug = 'tnpsc' AND (official_site_url IS NULL OR official_site_url = '')",
        "UPDATE exams SET official_site_url = 'https://www.upsc.gov.in' WHERE slug = 'upsc' AND (official_site_url IS NULL OR official_site_url = '')",
        "UPDATE exams SET official_site_url = 'https://jeemain.nta.nic.in' WHERE slug = 'jee' AND (official_site_url IS NULL OR official_site_url = '')",
        "UPDATE exams SET official_site_url = 'https://neet.nta.nic.in' WHERE slug = 'neet' AND (official_site_url IS NULL OR official_site_url = '')",
        "ALTER TABLE papers MODIFY COLUMN download_count INT NOT NULL DEFAULT 0",
        "ALTER TABLE papers MODIFY COLUMN pdf_url VARCHAR(500) NULL",
        "CREATE TABLE IF NOT EXISTS notifications (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NULL, title VARCHAR(255) NOT NULL, message TEXT NOT NULL, paper_id INT NULL, exam_slug VARCHAR(50) NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS user_notification_reads (user_id INT NOT NULL, notification_id INT NOT NULL, read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id, notification_id))",
        "INSERT INTO users (name, email, password_hash, role) VALUES ('Admin', 'admin@examvault.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCgRbDExgr5VhVcH9yDFMhS', 'admin') ON DUPLICATE KEY UPDATE role = 'admin'",
    ]

    for stmt in statements:
        try:
            with conn.cursor() as cur:
                cur.execute(stmt)
            conn.commit()
        except Exception:
            conn.rollback()
            
    _SCHEMA_CHECKED = True


def get_db():
    """
    Return the per-request PyMySQL connection from Flask's g.
    Creates a new connection on first call within a request context.
    """
    if "db" not in g:
        from flask import current_app
        params = _parse_url(current_app.config["DATABASE_URL"])
        g.db = pymysql.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        _ensure_schema(g.db)
    return g.db


def close_db(e=None):
    """Teardown: close the connection at the end of each request."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    """Register close_db as a teardown handler on the Flask app."""
    app.teardown_appcontext(close_db)
