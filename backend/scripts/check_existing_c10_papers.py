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
        SELECT ec.name as category_name, p.year, s.name as subject_name, COUNT(*) as cnt
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        LEFT JOIN paper_subjects ps ON p.id = ps.paper_id
        LEFT JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.id IN (64, 67, 2626)
        GROUP BY ec.name, p.year, s.name
        ORDER BY ec.name, s.name, p.year DESC
    """)
    rows = cur.fetchall()
    print(f"Total grouped rows: {len(rows)}")
    for r in rows:
        print(f"  [{r['category_name']}] {r['subject_name'] or 'NO SUBJECT'} - {r['year']}: {r['cnt']} papers")

conn.close()
