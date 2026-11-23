import os
import pymysql
import urllib.request
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
        SELECT p.id, p.year, p.title, p.pdf_url
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE ec.slug = 'cbse-10' AND (p.pdf_url LIKE 'http://%' OR p.pdf_url LIKE 'https://%')
    """)
    remote_papers = cur.fetchall()

print(f"Total remote URL papers in CBSE Class 10: {len(remote_papers)}")

broken_remote = []
for p in remote_papers:
    url = p['pdf_url']
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                broken_remote.append((p['id'], p['year'], p['title'], url, resp.status))
    except Exception as e:
        broken_remote.append((p['id'], p['year'], p['title'], url, str(e)))

print(f"Total broken remote URLs in CBSE Class 10: {len(broken_remote)}")
for b in broken_remote[:30]:
    print("  Broken:", b)
