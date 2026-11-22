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
        SELECT s.name as subject_name, p.year, COUNT(*) as cnt
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        LEFT JOIN paper_subjects ps ON p.id = ps.paper_id
        LEFT JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.id = 64 AND s.name IN ('Mathematics', 'Science', 'English', 'Social Science', 'Tamil')
        GROUP BY s.name, p.year
        ORDER BY s.name, p.year DESC
    """)
    rows = cur.fetchall()
    print("=== CBSE CLASS 10 CORE 5 SUBJECTS ===")
    for r in rows:
        print(f"  {r['subject_name']} - {r['year']}: {r['cnt']} papers")

conn.close()
