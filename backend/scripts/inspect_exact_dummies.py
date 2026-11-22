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

upload_dir = 'f:/exam/backend/uploads'

with conn.cursor() as cur:
    cur.execute("""
        SELECT p.id, p.title, p.year, p.pdf_url, ec.slug as cat_slug, s.name as subject_name
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        LEFT JOIN paper_subjects ps ON p.id = ps.paper_id
        LEFT JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.slug IN ('cbse-10', 'tn-sslc')
    """)
    rows = cur.fetchall()

dummies = []
for r in rows:
    url = r['pdf_url'] or ''
    is_dummy = False
    sz = 0
    if url.startswith('/uploads/'):
        rel = url[len('/uploads/'):]
        fp = os.path.join(upload_dir, rel.replace('/', os.sep))
        if os.path.exists(fp):
            sz = os.path.getsize(fp)
            if sz < 1000:
                is_dummy = True
        else:
            is_dummy = True
            sz = -1
    elif not url:
        is_dummy = True

    if is_dummy:
        dummies.append((r['id'], r['cat_slug'], r['year'], r['subject_name'], r['title'], url, sz))

print(f"Total dummy rows in cbse-10 & tn-sslc: {len(dummies)}")
for d in dummies:
    print(d)
