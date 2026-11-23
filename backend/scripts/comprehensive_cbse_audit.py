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
        SELECT ec.slug as cat_slug, p.year, count(*) as count,
               sum(case when p.file_size > 5000 then 1 else 0 end) as valid_files,
               sum(case when p.has_answer_key = 1 then 1 else 0 end) as keys_count
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE ec.slug IN ('cbse-10', 'cbse-12')
        GROUP BY ec.slug, p.year
        ORDER BY ec.slug, p.year DESC
    """)
    rows = cur.fetchall()

print("=== CBSE PAPERS BREAKDOWN BY CATEGORY AND YEAR ===")
for r in rows:
    print(f"[{r['cat_slug']}] Year {r['year']}: Total={r['count']} | Valid(>5KB)={r['valid_files']} | Keys={r['keys_count']}")

# Also let's check core subjects year by year
print("\n=== CBSE 10 CORE SUBJECTS BREAKDOWN ===")
with conn.cursor() as cur:
    cur.execute("""
        SELECT s.name as subject_name, p.year, count(*) as count,
               sum(case when p.file_size > 5000 then 1 else 0 end) as valid_files
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.slug = 'cbse-10'
          AND s.name IN ('Mathematics', 'Science', 'Social Science', 'English', 'Tamil', 'Hindi')
        GROUP BY s.name, p.year
        ORDER BY s.name, p.year DESC
    """)
    rows10 = cur.fetchall()

for r in rows10:
    print(f"{r['subject_name']} | {r['year']}: {r['count']} papers (valid: {r['valid_files']})")

print("\n=== CBSE 12 CORE SUBJECTS BREAKDOWN ===")
with conn.cursor() as cur:
    cur.execute("""
        SELECT s.name as subject_name, p.year, count(*) as count,
               sum(case when p.file_size > 5000 then 1 else 0 end) as valid_files
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.slug = 'cbse-12'
          AND s.name IN ('Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'Computer Science')
        GROUP BY s.name, p.year
        ORDER BY s.name, p.year DESC
    """)
    rows12 = cur.fetchall()

for r in rows12:
    print(f"{r['subject_name']} | {r['year']}: {r['count']} papers (valid: {r['valid_files']})")
