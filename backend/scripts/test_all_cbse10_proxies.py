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
        WHERE ec.slug = 'cbse-10'
        ORDER BY p.id ASC
    """)
    papers = cur.fetchall()

print(f"Total CBSE Class 10 papers: {len(papers)}")

failed_urls = []
for p in papers:
    url = p['pdf_url'] or ''
    # Test proxy URL locally
    test_proxy = f"http://localhost:5000/papers/proxy-pdf?url={urllib.parse.quote(url, safe='')}"
    try:
        req = urllib.request.Request(test_proxy)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            if len(data) < 500 or b'Failed to retrieve' in data:
                failed_urls.append((p['id'], p['year'], p['title'], url, f"Size {len(data)}"))
    except Exception as e:
        failed_urls.append((p['id'], p['year'], p['title'], url, str(e)))

print(f"Total failed URLs in CBSE Class 10: {len(failed_urls)}")
for f in failed_urls[:20]:
    print("  Failed:", f)
