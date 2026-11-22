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
        SELECT ec.slug as cat_slug, s.name as subject_name,
               count(*) as total_papers,
               min(p.year) as min_year,
               max(p.year) as max_year,
               count(distinct p.year) as distinct_years
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.slug IN ('cbse-10', 'tn-sslc')
          AND s.name IN ('Mathematics', 'Science', 'Social Science', 'English', 'Tamil')
        GROUP BY ec.slug, s.name
        ORDER BY ec.slug, s.name
    """)
    rows = cur.fetchall()

print("=== CLASS 10 CORE SUBJECTS SUMMARY ===")
for r in rows:
    cat = r['cat_slug']
    sub = r['subject_name']
    tot = r['total_papers']
    min_yr = r['min_year']
    max_yr = r['max_year']
    num_yrs = r['distinct_years']
    print(f"[{cat}] {sub}: {tot} papers across {num_yrs} years ({min_yr} to {max_yr})")

print("\n=== VERIFYING FILE EXISTENCE & VALIDITY ON DISK ===")
upload_dir = 'f:/exam/backend/uploads'
with conn.cursor() as cur:
    cur.execute("""
        SELECT p.id, p.title, p.pdf_url, p.file_size, ec.slug as cat_slug, s.name as sub, p.year
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.slug IN ('cbse-10', 'tn-sslc')
          AND s.name IN ('Mathematics', 'Science', 'Social Science', 'English', 'Tamil')
    """)
    all_papers = cur.fetchall()

invalid = 0
valid = 0
for p in all_papers:
    url = p['pdf_url'] or ''
    if url.startswith('/uploads/'):
        rel = url[len('/uploads/'):]
        fp = os.path.join(upload_dir, rel.replace('/', os.sep))
        if not os.path.exists(fp) or os.path.getsize(fp) < 5000:
            invalid += 1
            print(f"  [INVALID] ID {p['id']}: {p['title']} ({url}) - size: {os.path.getsize(fp) if os.path.exists(fp) else 'MISSING'}")
        else:
            valid += 1
    elif url.startswith('http'):
        valid += 1

print(f"File validation: {valid} VALID files (> 5 KB), {invalid} INVALID files")
