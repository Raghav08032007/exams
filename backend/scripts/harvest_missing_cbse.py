import os
import sys
import json
import urllib.request
import pymysql
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv('f:/exam/backend/.env')
db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)
conn = pymysql.connect(
    host=parsed.hostname or 'localhost',
    port=parsed.port or 3306,
    user=parsed.username or 'root',
    password=parsed.password or '',
    database=parsed.path.lstrip('/') or 'examvault',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

UPLOAD_DIR = 'f:/exam/backend/uploads/papers'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 5000:
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read()
            if len(content) > 1000 and content.startswith(b'%PDF'):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

# 1. Harvest Class 12 CS from gadepall/cbse-papers
cs_papers = [
    ("2021", "https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/cs/2021.pdf"),
    ("2019", "https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/cs/2019.pdf"),
    ("2018", "https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/cs/2018.pdf"),
    ("2017", "https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/cs/2017.pdf"),
    ("2016", "https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/cs/2016.pdf"),
    ("2015", "https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/cs/2015.pdf"),
    ("2013", "https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/cs/2013.pdf")
]

# Find CBSE 12 category and CS subject
with conn.cursor() as cur:
    cur.execute("SELECT id FROM exam_categories WHERE slug = 'cbse-12'")
    c12_cat = cur.fetchone()['id']
    cur.execute("SELECT id FROM subjects WHERE name = 'Computer Science'")
    cs_row = cur.fetchone()
    if not cs_row:
        cur.execute("INSERT INTO subjects (name, code) VALUES ('Computer Science', '083')")
        cs_subj_id = cur.lastrowid
    else:
        cs_subj_id = cs_row['id']

print("--- Harvesting Class 12 Computer Science papers ---")
for yr, url in cs_papers:
    filename = f"cbse12_{yr}_computerscience.pdf"
    target = os.path.join(UPLOAD_DIR, 'cbse-12', filename)
    if download_file(url, target):
        sz = os.path.getsize(target)
        web_path = f"/uploads/papers/cbse-12/{filename}"
        title = f"CBSE Class 12 {yr} — Computer Science Official Question Paper"
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM papers 
                WHERE exam_category_id = %s AND year = %s AND title LIKE %s
            """, (c12_cat, yr, '%Computer Science%'))
            existing = cur.fetchone()
            if not existing:
                cur.execute("""
                    INSERT INTO papers (
                        exam_category_id, year, title, language, pdf_url, file_size,
                        source_url, source_name, paper_type, verification_status
                    ) VALUES (%s, %s, %s, 'English', %s, %s, %s, 'gadepall/cbse-papers', 'original', 'verified')
                """, (c12_cat, yr, title, web_path, sz, url))
                p_id = cur.lastrowid
                cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (p_id, cs_subj_id))
                print(f"Added: {title} ({sz} bytes)")
            else:
                cur.execute("UPDATE papers SET pdf_url = %s, file_size = %s, verification_status = 'verified' WHERE id = %s", (web_path, sz, existing['id']))
                print(f"Updated: {title} (ID {existing['id']})")

print("Class 12 CS harvesting complete!")
