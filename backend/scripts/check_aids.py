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
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

with conn.cursor() as cur:
    cur.execute("SELECT id, exam_category_id, year, title FROM papers WHERE pdf_url LIKE '%aid=3843%' OR pdf_url LIKE '%aid=387%'")
    rows = cur.fetchall()
    print(f"Matched {len(rows)} rows:")
    for r in rows:
        print(r)

conn.close()
