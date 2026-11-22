"""
Migration script for Phase 1: Create 'textbooks' table in MySQL examvault.
"""
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "261008",
    "database": "examvault",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True
}

def migrate_database():
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        print("Checking/creating 'textbooks' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS textbooks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                standard_level VARCHAR(20) NOT NULL COMMENT 'e.g. "Class 1" to "Class 12"',
                board VARCHAR(50) NOT NULL COMMENT 'e.g. "CBSE / NCERT", "Tamil Nadu State Board"',
                subject_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                edition_year SMALLINT NULL DEFAULT 2024,
                language VARCHAR(50) NOT NULL DEFAULT 'English',
                pdf_url VARCHAR(500) NOT NULL,
                cover_image_url VARCHAR(500) NULL,
                chapter_number TINYINT NULL,
                chapter_title VARCHAR(255) NULL,
                source_url VARCHAR(500) NULL,
                source_name VARCHAR(100) NULL,
                download_count INT NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                INDEX ix_textbooks_standard (standard_level),
                INDEX ix_textbooks_board (board),
                INDEX ix_textbooks_subject_id (subject_id),
                INDEX ix_textbooks_language (language)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        print("'textbooks' table is ready.")

        # Ensure school exams/standards exist in exams table if needed
        cur.execute("SELECT id, slug, name FROM exams")
        existing_exams = {e['slug']: e['id'] for e in cur.fetchall()}
        print(f"Existing exams in database: {list(existing_exams.keys())}")

    conn.close()

if __name__ == "__main__":
    migrate_database()
