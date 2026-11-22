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
        SELECT p.id, p.year, p.title, p.pdf_url, p.source_name, p.source_url
        FROM papers p
        WHERE p.source_name LIKE '%CBSE Official Examination Board Archive%'
           OR p.source_name LIKE '%CBSE%'
        LIMIT 20
    """)
    rows = cur.fetchall()
    print(f"Matched {len(rows)} rows:")
    for r in rows:
        print(f"  id: {r['id']}, title: {r['title'][:60]}, url: {r['pdf_url']}")

conn.close()
