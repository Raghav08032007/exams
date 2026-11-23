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
        SELECT p.id, p.year, p.title, p.pdf_url
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE ec.slug = 'cbse-10'
    """)
    papers = cur.fetchall()

remote_list = [p for p in papers if p['pdf_url'] and p['pdf_url'].startswith('http')]
print(f"Total CBSE Class 10 papers: {len(papers)}, Remote count: {len(remote_list)}")
domains = {}
for p in remote_list:
    d = urlparse(p['pdf_url']).netloc
    domains[d] = domains.get(d, 0) + 1
print("Remote domains:", domains)
print("\nFirst 10 remote papers:")
for p in remote_list[:10]:
    print(f"  ID {p['id']}: {p['title']} -> {p['pdf_url']}")
