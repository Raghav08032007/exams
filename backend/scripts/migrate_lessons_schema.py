"""
Migration script: create `chapters` and `chapter_questions` tables in MySQL.
Enables chapter-wise / lesson-wise segregation of subjects, linking textbook
content directly to curated questions from Oswaal, NCERT Exemplar, and PYQ archives.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.db import get_db

app = create_app()

def migrate():
    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            print("Creating `chapters` table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_slug VARCHAR(50) NOT NULL,
                    standard_level VARCHAR(50) NOT NULL,
                    subject_id INT NOT NULL,
                    board VARCHAR(100) NOT NULL DEFAULT 'CBSE / NCERT',
                    chapter_number INT NOT NULL,
                    chapter_title VARCHAR(255) NOT NULL,
                    textbook_id INT NULL,
                    textbook_chapter_url VARCHAR(500) NULL,
                    summary_notes TEXT NULL,
                    marks_weightage VARCHAR(50) NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_exam_std_subj (exam_slug, standard_level, subject_id),
                    CONSTRAINT fk_chapter_subject FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            print("Creating `chapter_questions` table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chapter_questions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    chapter_id INT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type VARCHAR(50) DEFAULT 'Short Answer',
                    marks INT DEFAULT 2,
                    answer_explanation TEXT NULL,
                    source_publication VARCHAR(255) NOT NULL DEFAULT 'Oswaal Question Bank / NCERT Exemplar',
                    difficulty VARCHAR(20) DEFAULT 'Medium',
                    year INT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_chapter_id (chapter_id),
                    CONSTRAINT fk_cq_chapter FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

        conn.commit()
        print("Migration successful! `chapters` and `chapter_questions` tables created.")

if __name__ == "__main__":
    migrate()
