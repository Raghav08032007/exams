import os, pymysql
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
        SELECT p.id, p.year, p.title, p.pdf_url, ec.slug as cat_slug
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE p.pdf_url LIKE '%gadepall/cbse-papers/main/20%'
    """)
    rows = cur.fetchall()

print(f"Total papers with gadepall/cbse-papers/main/20...: {len(rows)}")
for r in rows:
    print(f"  ID {r['id']} ({r['cat_slug']} {r['year']}): {r['title']} -> {r['pdf_url']}")
