import os
import pymysql
import urllib.request
import urllib.parse
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
    """)
    papers = cur.fetchall()

print(f"Total CBSE Class 10 papers: {len(papers)}")

url_types = {}
for p in papers:
    u = p['pdf_url'] or ''
    if u.startswith('/uploads/'):
        prefix = 'local_uploads'
    elif 'raw.githubusercontent.com' in u:
        prefix = 'github_raw'
    elif 'boards10.github.io' in u:
        prefix = 'boards10'
    elif u.startswith('http'):
        prefix = 'other_http'
    else:
        prefix = 'empty_or_other'
    url_types[prefix] = url_types.get(prefix, 0) + 1

print("URL Breakdown for CBSE Class 10:", url_types)

# Let's test a sample from each type
for p in papers:
    u = p['pdf_url'] or ''
    if 'raw.githubusercontent.com' in u or prefix == 'other_http':
        # test proxy
        encoded = urllib.parse.quote(u, safe='')
        test_url = f"http://127.0.0.1:5000/papers/proxy-pdf?url={encoded}"
        try:
            req = urllib.request.Request(test_url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read()
                if b'error' in content:
                    print(f"FAILED GITHUB RAW: ID {p['id']} - {p['title']} - URL: {u}")
                    print(f"   Response: {content.decode('utf-8', errors='ignore')}")
                    break
        except Exception as e:
            print(f"EXCEPTION GITHUB RAW: ID {p['id']} - {p['title']} - URL: {u} - {e}")
            break
