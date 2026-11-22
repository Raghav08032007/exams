import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "261008")
DB_NAME = os.getenv("MYSQL_DB", "examvault")

def migrate():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cur:
        # 1. User Revision Notes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                paper_id INT NOT NULL,
                note_text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
                UNIQUE KEY uq_user_paper_note (user_id, paper_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✓ Created or verified `user_notes` table")

        # 2. Practice Attempts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS practice_attempts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                paper_id INT NOT NULL,
                duration_seconds INT NOT NULL,
                self_score DECIMAL(5,2) NULL,
                max_score DECIMAL(5,2) NULL,
                notes TEXT NULL,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
                INDEX ix_user_practice (user_id),
                INDEX ix_paper_practice (paper_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✓ Created or verified `practice_attempts` table")

    conn.commit()
    conn.close()
    print("Migration finished successfully.")

if __name__ == "__main__":
    migrate()
