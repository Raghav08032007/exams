import os
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
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT p.id, p.year, p.title, p.pdf_url
        FROM papers p
        WHERE p.exam_category_id = 64 AND (p.pdf_url LIKE 'http://%' OR p.pdf_url LIKE 'https://%')
    """)
    broken = cur.fetchall()

print(f"Found {len(broken)} broken remote placeholder records in CBSE Class 10 to purge.")
for b in broken[:15]:
    print("  To purge:", b['id'], b['year'], b['title'])

if broken:
    ids = [b['id'] for b in broken]
    fmt = ",".join(["%s"] * len(ids))
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM paper_subjects WHERE paper_id IN ({fmt})", ids)
        cur.execute(f"DELETE FROM user_notes WHERE paper_id IN ({fmt})", ids)
        cur.execute(f"DELETE FROM practice_attempts WHERE paper_id IN ({fmt})", ids)
        cur.execute(f"DELETE FROM bookmarks WHERE paper_id IN ({fmt})", ids)
        cur.execute(f"DELETE FROM papers WHERE id IN ({fmt})", ids)
    conn.commit()
    print("Successfully purged all broken placeholder records!")
