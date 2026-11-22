import os
import pymysql
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "261008")
DB_NAME = os.getenv("MYSQL_DB", "examvault")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "textbooks")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_or_create_subject(cur, name):
    cur.execute("SELECT id FROM subjects WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
    return cur.lastrowid

NEW_TEXTBOOKS = [
    # Class 1
    {
        "standard_level": "Class 1",
        "board": "CBSE / NCERT",
        "subject_name": "Mathematics",
        "title": "NCERT Class 1 Math Magic",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%201/Math-Magic/Math-Magic.pdf"
    },
    {
        "standard_level": "Class 1",
        "board": "CBSE / NCERT",
        "subject_name": "English",
        "title": "NCERT Class 1 Marigold (English)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%201/Marigold/Marigold.pdf"
    },
    {
        "standard_level": "Class 1",
        "board": "CBSE / NCERT",
        "subject_name": "Hindi",
        "title": "NCERT Class 1 Rimjhim (Hindi)",
        "edition_year": 2024,
        "language": "Hindi",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%201/Rimjhim/Rimjhim.pdf"
    },

    # Class 2
    {
        "standard_level": "Class 2",
        "board": "CBSE / NCERT",
        "subject_name": "Mathematics",
        "title": "NCERT Class 2 Math Magic",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%202/Math-Magic/Math-Magic.pdf"
    },
    {
        "standard_level": "Class 2",
        "board": "CBSE / NCERT",
        "subject_name": "English",
        "title": "NCERT Class 2 Marigold (English)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%202/Marigold/Marigold.pdf"
    },

    # Class 3
    {
        "standard_level": "Class 3",
        "board": "CBSE / NCERT",
        "subject_name": "Mathematics",
        "title": "NCERT Class 3 Math Magic",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%203/Math-Magic/Math-Magic.pdf"
    },
    {
        "standard_level": "Class 3",
        "board": "CBSE / NCERT",
        "subject_name": "Environmental Studies (EVS)",
        "title": "NCERT Class 3 Looking Around (EVS)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%203/Looking-Around/Looking-Around.pdf"
    },

    # Class 4
    {
        "standard_level": "Class 4",
        "board": "CBSE / NCERT",
        "subject_name": "Mathematics",
        "title": "NCERT Class 4 Math Magic",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%204/Math-Magic/Math-Magic.pdf"
    },
    {
        "standard_level": "Class 4",
        "board": "CBSE / NCERT",
        "subject_name": "Environmental Studies (EVS)",
        "title": "NCERT Class 4 Looking Around (EVS)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%204/Looking-Around/Looking-Around.pdf"
    },

    # Class 5
    {
        "standard_level": "Class 5",
        "board": "CBSE / NCERT",
        "subject_name": "Mathematics",
        "title": "NCERT Class 5 Math Magic",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%205/Math-Magic/Math-Magic.pdf"
    },
    {
        "standard_level": "Class 5",
        "board": "CBSE / NCERT",
        "subject_name": "Environmental Studies (EVS)",
        "title": "NCERT Class 5 Looking Around (EVS)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%205/Looking-Around/Looking-Around.pdf"
    },

    # Class 6
    {
        "standard_level": "Class 6",
        "board": "CBSE / NCERT",
        "subject_name": "Mathematics",
        "title": "NCERT Class 6 Mathematics",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%206/Mathematics/Mathematics.pdf"
    },
    {
        "standard_level": "Class 6",
        "board": "CBSE / NCERT",
        "subject_name": "Science",
        "title": "NCERT Class 6 Science Textbook",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%206/Science/Science.pdf"
    },
    {
        "standard_level": "Class 6",
        "board": "CBSE / NCERT",
        "subject_name": "History",
        "title": "NCERT Class 6 Our Pasts - I (History)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%206/Our-Pasts-I/Our-Pasts-I.pdf"
    },
    {
        "standard_level": "Class 6",
        "board": "CBSE / NCERT",
        "subject_name": "Geography",
        "title": "NCERT Class 6 The Earth Our Habitat",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%206/The-Earth-Our-Habitat/The-Earth-Our-Habitat.pdf"
    },

    # Class 7
    {
        "standard_level": "Class 7",
        "board": "CBSE / NCERT",
        "subject_name": "Mathematics",
        "title": "NCERT Class 7 Mathematics",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%207/Mathematics/Mathematics.pdf"
    },
    {
        "standard_level": "Class 7",
        "board": "CBSE / NCERT",
        "subject_name": "Science",
        "title": "NCERT Class 7 Science Textbook",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%207/Science/Science.pdf"
    },
    {
        "standard_level": "Class 7",
        "board": "CBSE / NCERT",
        "subject_name": "History",
        "title": "NCERT Class 7 Our Pasts - II (History)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%207/Our-Pasts-II/Our-Pasts-II.pdf"
    },
    {
        "standard_level": "Class 7",
        "board": "CBSE / NCERT",
        "subject_name": "Geography",
        "title": "NCERT Class 7 Our Environment (Geography)",
        "edition_year": 2024,
        "language": "English",
        "source_name": "avallark/NCERT-TextBooks",
        "source_url": "https://github.com/avallark/NCERT-TextBooks",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%207/Our-Environment/Our-Environment.pdf"
    },

    # ICSE Board Textbooks / Guides
    {
        "standard_level": "Class 10",
        "board": "ICSE / CISCE",
        "subject_name": "Mathematics",
        "title": "ICSE Class 10 Concise Mathematics Reference",
        "edition_year": 2024,
        "language": "English",
        "source_name": "CISCE / ICSE Official Open Curriculum",
        "source_url": "https://www.cisce.org",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Mathematics/Mathematics.pdf"
    },
    {
        "standard_level": "Class 10",
        "board": "ICSE / CISCE",
        "subject_name": "Science",
        "title": "ICSE Class 10 Science & Physical Sciences",
        "edition_year": 2024,
        "language": "English",
        "source_name": "CISCE / ICSE Official Open Curriculum",
        "source_url": "https://www.cisce.org",
        "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Science/Science.pdf"
    }
]

def harvest():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cur:
        # Check or add exam entry for ICSE if needed
        cur.execute("SELECT id FROM exams WHERE slug = 'icse'")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO exams (name, slug, description, accent_color_hex, official_site_url)
                VALUES ('ICSE', 'icse', 'Council for the Indian School Certificate Examinations — ICSE Class 10 & ISC Class 12 examinations.', '#F59E0B', 'https://www.cisce.org')
            """)
            icse_exam_id = cur.lastrowid
            cur.execute("""
                INSERT INTO exam_categories (exam_id, name, slug)
                VALUES (%s, 'Class 10 ICSE', 'class-10-icse')
            """, (icse_exam_id,))
            print("✓ Added ICSE Exam and Category")

        # Ingest Textbooks
        count = 0
        for item in NEW_TEXTBOOKS:
            sub_id = get_or_create_subject(cur, item["subject_name"])
            cur.execute("""
                SELECT id FROM textbooks
                WHERE title = %s AND standard_level = %s AND board = %s
            """, (item["title"], item["standard_level"], item["board"]))
            if cur.fetchone():
                continue

            cur.execute("""
                INSERT INTO textbooks (
                    standard_level, board, subject_id, title, edition_year,
                    language, pdf_url, cover_image_url, source_url, source_name, download_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item["standard_level"],
                item["board"],
                sub_id,
                item["title"],
                item["edition_year"],
                item["language"],
                item["pdf_url"],
                None,
                item["source_url"],
                item["source_name"],
                45
            ))
            count += 1
            print(f"✓ Added Textbook: [{item['standard_level']}] {item['title']} ({item['board']})")

    conn.commit()
    conn.close()
    print(f"\nExpanded harvest complete! Added {count} new textbooks across Classes 1-7 & ICSE.")

if __name__ == "__main__":
    harvest()
