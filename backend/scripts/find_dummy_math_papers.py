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
        SELECT p.id, p.year, p.session, p.title, p.pdf_url
        FROM papers p
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        WHERE p.exam_category_id = 64
          AND s.name = 'Mathematics'
          AND p.pdf_url LIKE '/uploads/cbse-10%'
        ORDER BY p.year DESC, p.id ASC
    """)
    rows = cur.fetchall()
    print(f"Dummy Math papers found: {len(rows)}")
    for r in rows:
        print(f"  id: {r['id']}, year: {r['year']}, session: {r['session']}, title: {r['title']}, url: {r['pdf_url']}")

conn.close()
