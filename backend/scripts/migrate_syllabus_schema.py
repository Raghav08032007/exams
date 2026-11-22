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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_syllabus_progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                exam_slug VARCHAR(50) NOT NULL,
                subject_name VARCHAR(100) NOT NULL,
                topic_name VARCHAR(255) NOT NULL,
                is_completed BOOLEAN NOT NULL DEFAULT 1,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY uq_user_topic (user_id, exam_slug, subject_name, topic_name),
                INDEX ix_user_exam (user_id, exam_slug)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✓ Created or verified `user_syllabus_progress` table")

    conn.commit()
    conn.close()
    print("Syllabus schema migration complete.")

if __name__ == "__main__":
    migrate()
