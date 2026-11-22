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
        SELECT s.name as subject, p.year, COUNT(*) as cnt
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.id = 67
        GROUP BY s.name, p.year
        ORDER BY s.name, p.year DESC
    """)
    rows = cur.fetchall()
    print("=== TN SSLC 10th (Category 67) VERIFIED BREAKDOWN ===")
    current_sub = None
    for r in rows:
        if r['subject'] != current_sub:
            current_sub = r['subject']
            print(f"\n[{current_sub}]")
        print(f"  {r['year']}: {r['cnt']} paper(s)")

conn.close()
