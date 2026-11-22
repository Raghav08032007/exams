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
        SELECT p.id, p.title, p.year, p.pdf_url, p.source_url, ec.slug as cat_slug
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE p.pdf_url LIKE '/uploads/%'
    """)
    rows = cur.fetchall()

upload_dir = 'f:/exam/backend/uploads'
dummies = []
for r in rows:
    rel = r['pdf_url'][len('/uploads/'):]
    fp = os.path.join(upload_dir, rel.replace('/', os.sep))
    if os.path.exists(fp):
        sz = os.path.getsize(fp)
        if sz < 1000:
            dummies.append((r['id'], r['year'], r['cat_slug'], r['title'], r['pdf_url'], sz))
    else:
        dummies.append((r['id'], r['year'], r['cat_slug'], r['title'], r['pdf_url'], -1))

print(f"Total dummy or missing papers: {len(dummies)}")
for d in dummies:
    print(d)
