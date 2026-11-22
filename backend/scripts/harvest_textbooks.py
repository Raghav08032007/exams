"""
Harvest and index official textbooks across Classes 1 to 12 into MySQL examvault.
"""
import os
import urllib.request
import urllib.parse
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

UPLOAD_TEXTBOOKS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "textbooks"
)
os.makedirs(UPLOAD_TEXTBOOKS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Catalog of verified textbooks
TEXTBOOK_CATALOG = [
    # ── CLASS 10 (NCERT / CBSE) ──────────────────────────────────────────
    {
        "standard_level": "Class 10",
        "board": "CBSE / NCERT",
        "subject": "Mathematics",
        "title": "NCERT Class 10 Mathematics Textbook",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 10",
        "board": "CBSE / NCERT",
        "subject": "Science",
        "title": "NCERT Class 10 Science Textbook",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Science.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 10",
        "board": "CBSE / NCERT",
        "subject": "Social Science",
        "title": "NCERT Class 10 Contemporary India II (Geography)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Contemporary-India-2.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 10",
        "board": "CBSE / NCERT",
        "subject": "Social Science",
        "title": "NCERT Class 10 Democratic Politics II (Polity)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Democratic-Politics-2.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 10",
        "board": "CBSE / NCERT",
        "subject": "History",
        "title": "NCERT Class 10 India and the Contemporary World II (History)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Indian-and-Contemporary-World-2.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 10",
        "board": "CBSE / NCERT",
        "subject": "Economics",
        "title": "NCERT Class 10 Understanding Economic Development",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Understanding-Economic-Development.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 10",
        "board": "CBSE / NCERT",
        "subject": "Mathematics",
        "title": "NCERT Class 10 Mathematics Exemplar Problems",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics-Problems.pdf",
        "source_name": "NCERT Exemplar Problem Series",
        "source_url": "https://ncert.nic.in/exemplar-problems.php"
    },

    # ── CLASS 9 (NCERT / CBSE) ───────────────────────────────────────────
    {
        "standard_level": "Class 9",
        "board": "CBSE / NCERT",
        "subject": "Mathematics",
        "title": "NCERT Class 9 Mathematics Textbook",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/9/9th-Mathematics.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 9",
        "board": "CBSE / NCERT",
        "subject": "Science",
        "title": "NCERT Class 9 Science Textbook",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/9/9th-Science.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 9",
        "board": "CBSE / NCERT",
        "subject": "Social Science",
        "title": "NCERT Class 9 Contemporary India I (Geography)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/9/9th-Contemporary-India.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 9",
        "board": "CBSE / NCERT",
        "subject": "Social Science",
        "title": "NCERT Class 9 Democratic Politics I (Polity)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/9/9th-Democratic-Politics.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 9",
        "board": "CBSE / NCERT",
        "subject": "Economics",
        "title": "NCERT Class 9 Economics Textbook",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/9/9th-Economics.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 9",
        "board": "CBSE / NCERT",
        "subject": "History",
        "title": "NCERT Class 9 India and the Contemporary World I (History)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/9/9th-Indian-and-the-Contemporary-World-1.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },

    # ── CLASS 8 (NCERT / CBSE) ───────────────────────────────────────────
    {
        "standard_level": "Class 8",
        "board": "CBSE / NCERT",
        "subject": "Geography",
        "title": "NCERT Class 8 Resources and Development (Geography)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/8/8th-Geography.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 8",
        "board": "CBSE / NCERT",
        "subject": "Social Science",
        "title": "NCERT Class 8 Social and Political Life III",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/8/8th-Social-and-Political-Life.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 8",
        "board": "CBSE / NCERT",
        "subject": "History",
        "title": "NCERT Class 8 Our Pasts III Volume 1",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/8/8th%20-%20Our%20Pasts%20Volume%201.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },

    # ── CLASS 11 (NCERT / CBSE) ──────────────────────────────────────────
    {
        "standard_level": "Class 11",
        "board": "CBSE / NCERT",
        "subject": "Polity",
        "title": "NCERT Class 11 Political Theory",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/11/11th-Political-Theory.pdf",
        "source_name": "NCERT Educational Repository",
        "source_url": "https://ncert.nic.in/textbook.php"
    },

    # ── CLASS 12 (NCERT / CBSE) ──────────────────────────────────────────
    {
        "standard_level": "Class 12",
        "board": "CBSE / NCERT",
        "subject": "Physics",
        "title": "NCERT Class 12 Physics Part 1",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/Class12_Physics_NCERT.pdf",
        "source_name": "NCERT Official Publication",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 12",
        "board": "CBSE / NCERT",
        "subject": "Chemistry",
        "title": "NCERT Class 12 Chemistry Part 1",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/Class12_Chemistry_NCERT.pdf",
        "source_name": "NCERT Official Publication",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 12",
        "board": "CBSE / NCERT",
        "subject": "Mathematics",
        "title": "NCERT Class 12 Mathematics Part 1",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/Class12_Maths_NCERT.pdf",
        "source_name": "NCERT Official Publication",
        "source_url": "https://ncert.nic.in/textbook.php"
    },
    {
        "standard_level": "Class 12",
        "board": "CBSE / NCERT",
        "subject": "Biology",
        "title": "NCERT Class 12 Biology Complete Book",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/Class12_Biology_NCERT.pdf",
        "source_name": "NCERT Official Publication",
        "source_url": "https://ncert.nic.in/textbook.php"
    },

    # ── TAMIL NADU STATE BOARD (SAMACHEER KALVI) ─────────────────────────
    {
        "standard_level": "Class 10",
        "board": "Tamil Nadu State Board",
        "subject": "Mathematics",
        "title": "Tamil Nadu SSLC Mathematics (Samacheer Kalvi)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/Tamil_Nadu/TN_10th_Maths_Textbook.pdf",
        "source_name": "TN Textbook Corporation",
        "source_url": "http://textbookcorp.tn.gov.in/"
    },
    {
        "standard_level": "Class 10",
        "board": "Tamil Nadu State Board",
        "subject": "Science",
        "title": "Tamil Nadu SSLC Science (Samacheer Kalvi)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/Tamil_Nadu/TN_10th_Science_Textbook.pdf",
        "source_name": "TN Textbook Corporation",
        "source_url": "http://textbookcorp.tn.gov.in/"
    },
    {
        "standard_level": "Class 10",
        "board": "Tamil Nadu State Board",
        "subject": "Social Science",
        "title": "Tamil Nadu SSLC Social Science (Samacheer Kalvi)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/Tamil_Nadu/TN_10th_SocialScience_Textbook.pdf",
        "source_name": "TN Textbook Corporation",
        "source_url": "http://textbookcorp.tn.gov.in/"
    },
    {
        "standard_level": "Class 12",
        "board": "Tamil Nadu State Board",
        "subject": "Physics",
        "title": "Tamil Nadu HSC Physics Volume 1 (Samacheer Kalvi)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/Tamil_Nadu/TN_12th_Physics_Vol1.pdf",
        "source_name": "TN Textbook Corporation",
        "source_url": "http://textbookcorp.tn.gov.in/"
    },
    {
        "standard_level": "Class 12",
        "board": "Tamil Nadu State Board",
        "subject": "Chemistry",
        "title": "Tamil Nadu HSC Chemistry Volume 1 (Samacheer Kalvi)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/Tamil_Nadu/TN_12th_Chemistry_Vol1.pdf",
        "source_name": "TN Textbook Corporation",
        "source_url": "http://textbookcorp.tn.gov.in/"
    },
    {
        "standard_level": "Class 12",
        "board": "Tamil Nadu State Board",
        "subject": "Accountancy",
        "title": "Tamil Nadu HSC Accountancy (Samacheer Kalvi)",
        "language": "English",
        "edition_year": 2024,
        "url": "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/Tamil_Nadu/TN_12th_Accountancy.pdf",
        "source_name": "TN Textbook Corporation",
        "source_url": "http://textbookcorp.tn.gov.in/"
    },
]

def download_file(url, out_path):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 500:
                with open(out_path, "wb") as f:
                    f.write(data)
                return True
    except Exception as e:
        # print(f"Download fail {url}: {e}")
        pass
    return False

def harvest_and_seed():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    print(f"Starting textbook ingestion for {len(TEXTBOOK_CATALOG)} standard textbooks...")
    success_count = 0

    for item in TEXTBOOK_CATALOG:
        # 1. Ensure subject exists
        cur.execute("SELECT id FROM subjects WHERE name = %s", (item["subject"],))
        subj = cur.fetchone()
        if not subj:
            cur.execute("INSERT INTO subjects (name) VALUES (%s)", (item["subject"],))
            subject_id = cur.lastrowid
        else:
            subject_id = subj["id"]

        # 2. Prepare local file
        std_clean = item["standard_level"].lower().replace(" ", "_")
        safe_name = "".join(c if c.isalnum() else "_" for c in item["title"])[:50]
        filename = f"{std_clean}_{safe_name}.pdf"
        local_path = os.path.join(UPLOAD_TEXTBOOKS_DIR, filename)
        rel_pdf_url = f"/uploads/textbooks/{filename}"

        # 3. Download if not exists
        if not os.path.exists(local_path) or os.path.getsize(local_path) < 1000:
            download_file(item["url"], local_path)

        # If file exists on disk, use relative url, else use direct CDN url
        final_pdf_url = rel_pdf_url if os.path.exists(local_path) and os.path.getsize(local_path) > 1000 else item["url"]

        # 4. Insert or update into textbooks table
        cur.execute("""
            INSERT INTO textbooks (
                standard_level, board, subject_id, title, edition_year,
                language, pdf_url, source_url, source_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                pdf_url = VALUES(pdf_url),
                source_url = VALUES(source_url)
        """, (
            item["standard_level"], item["board"], subject_id, item["title"],
            item["edition_year"], item["language"], final_pdf_url,
            item["source_url"], item["source_name"]
        ))
        success_count += 1
        print(f" [OK] {item['standard_level']} {item['board']} - {item['title'][:40]}")

    cur.execute("SELECT standard_level, board, COUNT(*) as count FROM textbooks GROUP BY standard_level, board")
    print("\nTextbook Summary by Standard and Board:")
    for row in cur.fetchall():
        print(f" - {row['standard_level']} [{row['board']}]: {row['count']} textbooks")

    cur.close()
    conn.close()

if __name__ == "__main__":
    harvest_and_seed()
