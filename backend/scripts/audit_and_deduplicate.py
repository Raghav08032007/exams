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

UPLOAD_DIR = 'f:/exam/backend/uploads'

print("=== 1. AUDITING VERIFICATION STATUS & PAPER TYPES ===")
with conn.cursor() as cur:
    cur.execute("""
        SELECT verification_status, paper_type, count(*) as count
        FROM papers
        GROUP BY verification_status, paper_type
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"Status: {r['verification_status']} | Type: {r['paper_type']} | Count: {r['count']}")

print("\n=== 2. CHECKING FOR DUPLICATES (Same Title, Category & Year) ===")
with conn.cursor() as cur:
    cur.execute("""
        SELECT exam_category_id, year, title, count(*) as cnt, GROUP_CONCAT(id) as ids
        FROM papers
        GROUP BY exam_category_id, year, title
        HAVING cnt > 1
        ORDER BY cnt DESC
    """)
    title_dupes = cur.fetchall()
    print(f"Total duplicate groups by title: {len(title_dupes)}")
    for d in title_dupes[:15]:
        print(f"  Category {d['exam_category_id']} | Year {d['year']} | Count {d['cnt']} | Title: '{d['title'][:40]}' | IDs: {d['ids']}")

print("\n=== 3. CHECKING FOR DUPLICATES (Same PDF URL in Same Category) ===")
with conn.cursor() as cur:
    cur.execute("""
        SELECT exam_category_id, pdf_url, count(*) as cnt, GROUP_CONCAT(id) as ids
        FROM papers
        WHERE pdf_url IS NOT NULL AND pdf_url != ''
        GROUP BY exam_category_id, pdf_url
        HAVING cnt > 1
        ORDER BY cnt DESC
    """)
    url_dupes = cur.fetchall()
    print(f"Total duplicate groups by pdf_url: {len(url_dupes)}")
    for u in url_dupes[:15]:
        print(f"  Category {u['exam_category_id']} | Count {u['cnt']} | URL: '{u['pdf_url'][:50]}' | IDs: {u['ids']}")

print("\n=== 4. CHECKING FILE SIZES & DUMMY/EMPTY FILES ON DISK ===")
with conn.cursor() as cur:
    cur.execute("""
        SELECT id, title, pdf_url, file_size, verification_status
        FROM papers
        WHERE pdf_url LIKE '/uploads/%'
    """)
    local_papers = cur.fetchall()

missing_or_tiny = []
for p in local_papers:
    rel = p['pdf_url'][len('/uploads/'):]
    fp = os.path.join(UPLOAD_DIR, rel.replace('/', os.sep))
    if not os.path.exists(fp):
        missing_or_tiny.append((p['id'], p['title'], 'MISSING FILE', p['pdf_url']))
    else:
        sz = os.path.getsize(fp)
        if sz < 1000:
            missing_or_tiny.append((p['id'], p['title'], f'TINY {sz}B', p['pdf_url']))

print(f"Total local papers: {len(local_papers)}")
print(f"Total missing or tiny (<1KB) local files: {len(missing_or_tiny)}")
for m in missing_or_tiny[:15]:
    print("  ", m)
