"""
Self-contained DB init & migration script.
Connects using DATABASE_URL in backend/.env, creates tables if missing,
applies column updates, and populates seed data.
"""
import os
import pymysql
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL", "mysql+pymysql://root:261008@localhost:3306/examvault")
for prefix in ("mysql+pymysql://", "mysql://", "pymysql://"):
    if db_url.startswith(prefix):
        db_url = "mysql://" + db_url[len(prefix):]
        break

parsed = urlparse(db_url)
host = parsed.hostname or "localhost"
port = parsed.port or 3306
user = parsed.username or "root"
password = parsed.password or ""
dbname = parsed.path.lstrip("/") or "examvault"

print(f"Connecting to MySQL server at {host}:{port} as user '{user}'...")

# Connect to MySQL server without database first to ensure DB exists
root_conn = pymysql.connect(
    host=host, port=port, user=user, password=password, charset="utf8mb4", autocommit=True
)
with root_conn.cursor() as cur:
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
root_conn.close()

# Connect to the target database
conn = pymysql.connect(
    host=host, port=port, user=user, password=password, database=dbname, charset="utf8mb4", autocommit=True
)

schema_statements = [
    """
    CREATE TABLE IF NOT EXISTS exams (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        slug VARCHAR(50) NOT NULL UNIQUE,
        description TEXT,
        accent_color_hex VARCHAR(7) NOT NULL,
        official_site_url VARCHAR(255) NULL,
        INDEX ix_exams_slug (slug)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('user', 'admin', 'verifier') NOT NULL DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX ix_users_email (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS exam_categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        exam_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        slug VARCHAR(100) NOT NULL,
        FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
        UNIQUE uq_category_exam_slug (exam_id, slug),
        INDEX ix_exam_categories_exam_id (exam_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS papers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        exam_category_id INT NOT NULL,
        year SMALLINT NOT NULL,
        session VARCHAR(50) NULL,
        title VARCHAR(255) NOT NULL,
        language VARCHAR(50) DEFAULT 'English',
        pdf_url VARCHAR(500),
        cover_image_url VARCHAR(500) NULL,
        file_size INT,
        has_answer_key BOOLEAN NOT NULL DEFAULT 0,
        answer_key_pdf_url VARCHAR(500),
        upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        download_count INT NOT NULL DEFAULT 0,
        verification_status VARCHAR(20) NOT NULL DEFAULT 'unverified',
        verified_by INT NULL,
        uploaded_by INT NULL,
        rejection_note TEXT NULL,
        FOREIGN KEY (exam_category_id) REFERENCES exam_categories(id) ON DELETE CASCADE,
        FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
        INDEX ix_papers_exam_category_id (exam_category_id),
        INDEX ix_papers_year (year),
        INDEX ix_papers_verification_status (verification_status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        paper_id INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
        UNIQUE uq_user_paper_bookmark (user_id, paper_id),
        INDEX ix_bookmarks_user_id (user_id),
        INDEX ix_bookmarks_paper_id (paper_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS paper_subjects (
        paper_id INT NOT NULL,
        subject_id INT NOT NULL,
        PRIMARY KEY (paper_id, subject_id),
        FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]

print("Applying schema tables...")
with conn.cursor() as cur:
    for sql in schema_statements:
        try:
            cur.execute(sql)
        except Exception as e:
            print(f"Table notice: {e}")

# Apply column updates for existing databases
alter_statements = [
    "ALTER TABLE users MODIFY COLUMN role ENUM('user', 'admin', 'verifier') NOT NULL DEFAULT 'user';",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS official_site_url VARCHAR(255) NULL;",
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS session VARCHAR(50) NULL AFTER year;",
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS uploaded_by INT NULL AFTER verified_by;",
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS cover_image_url VARCHAR(500) NULL AFTER pdf_url;",
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS source_url VARCHAR(500) NULL AFTER download_count;",
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS source_name VARCHAR(100) NULL AFTER source_url;",
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS answer_key_source_url VARCHAR(500) NULL AFTER source_name;",
]

with conn.cursor() as cur:
    for sql in alter_statements:
        try:
            cur.execute(sql)
        except Exception as e:
            pass

# Seed default exams if empty
seed_exams = [
    ('TNPSC', 'tnpsc', 'Tamil Nadu Public Service Commission — Group 1, 2A, 2, 4, and VAO examinations.', '#E8998D', 'https://www.tnpsc.gov.in'),
    ('UPSC',  'upsc',  'Union Public Service Commission — Civil Services Examination (Prelims & Mains).', '#8FB9A8', 'https://www.upsc.gov.in'),
    ('JEE',   'jee',   'Joint Entrance Examination — JEE Main (multiple sessions) and JEE Advanced.', '#8FB8E0', 'https://jeemain.nta.nic.in'),
    ('NEET',  'neet',  'National Eligibility cum Entrance Test — undergraduate medical admissions.', '#C3A8D9', 'https://neet.nta.nic.in'),
    ('Class 10', 'class-10', '10th Standard Board Exams — CBSE Class 10 and Tamil Nadu State Board (SSLC).', '#0D9488', 'https://www.cbse.gov.in'),
    ('Class 12', 'class-12', '12th Standard Board Exams — CBSE Class 12 and Tamil Nadu State Board (HSC).', '#E11D48', 'https://www.cbse.gov.in'),
]

with conn.cursor() as cur:
    for name, slug, desc, color, url in seed_exams:
        cur.execute("""
            INSERT INTO exams (name, slug, description, accent_color_hex, official_site_url)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              official_site_url = VALUES(official_site_url),
              accent_color_hex = VALUES(accent_color_hex),
              description = VALUES(description)
        """, (name, slug, desc, color, url))

# Seed default exam categories
seed_categories = [
    ('tnpsc', 'Group 1', 'group-1'),
    ('tnpsc', 'Group 2A', 'group-2a'),
    ('tnpsc', 'Group 2', 'group-2'),
    ('tnpsc', 'Group 4', 'group-4'),
    ('tnpsc', 'VAO', 'vao'),
    ('upsc',  'Prelims', 'prelims'),
    ('upsc',  'Mains', 'mains'),
    ('jee',   'JEE Main', 'jee-main'),
    ('jee',   'JEE Advanced', 'jee-advanced'),
    ('neet',  'NEET UG', 'neet-ug'),
    ('class-10', 'CBSE Class 10', 'cbse-10'),
    ('class-10', 'TN SSLC 10th', 'tn-sslc'),
    ('class-12', 'CBSE Class 12', 'cbse-12'),
    ('class-12', 'TN HSC 12th', 'tn-hsc'),
]

with conn.cursor() as cur:
    for exam_slug, cat_name, cat_slug in seed_categories:
        cur.execute("SELECT id FROM exams WHERE slug = %s", (exam_slug,))
        exam = cur.fetchone()
        if exam:
            cur.execute("""
                INSERT INTO exam_categories (exam_id, name, slug)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """, (exam[0], cat_name, cat_slug))

# Seed default admin user
# Password: Admin@1234
admin_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCgRbDExgr5VhVcH9yDFMhS"
with conn.cursor() as cur:
    cur.execute("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ('Admin', 'admin@examvault.in', %s, 'admin')
        ON DUPLICATE KEY UPDATE role = 'admin'
    """, (admin_hash,))

print("Database init & migration complete!")
conn.close()
