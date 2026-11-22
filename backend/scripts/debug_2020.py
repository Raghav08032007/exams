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
    cur.execute("SELECT id, exam_category_id, year, title, pdf_url FROM papers WHERE year = 2020 AND exam_category_id = 67")
    rows = cur.fetchall()
    print("Papers 2020 under category 67:", len(rows))
    for r in rows:
        print(r)
        cur.execute("SELECT * FROM paper_subjects WHERE paper_id = %s", (r['id'],))
        print("  Subjects linked:", cur.fetchall())

conn.close()
