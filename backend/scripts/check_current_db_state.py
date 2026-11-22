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
    cur.execute("SELECT id, slug, name FROM exams")
    exams = cur.fetchall()
    print("=== EXAMS ===")
    for e in exams:
        print(f"  {e['id']}: {e['slug']} - {e['name']}")

    cur.execute("SELECT id, slug, name FROM subjects")
    subs = cur.fetchall()
    print(f"\n=== SUBJECTS ({len(subs)} total) ===")
    for s in subs:
        print(f"  {s['id']}: {s['slug']} - {s['name']}")

    cur.execute("""
        SELECT e.slug, p.standard, COUNT(*) as cnt 
        FROM papers p 
        JOIN exams e ON p.exam_id = e.id 
        GROUP BY e.slug, p.standard
        ORDER BY e.slug, p.standard
    """)
    papers_breakdown = cur.fetchall()
    print("\n=== PAPERS PER EXAM & STANDARD ===")
    for row in papers_breakdown:
        print(f"  {row['slug']} (std: {row['standard']}): {row['cnt']} papers")

    cur.execute("""
        SELECT s.name as subject_name, p.standard, p.year, COUNT(*) as cnt
        FROM papers p
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        JOIN exams e ON p.exam_id = e.id
        WHERE p.standard = 10 AND e.slug IN ('cbse-10', 'cbse-12', 'state-boards', 'tn-sslc')
        GROUP BY s.name, p.standard, p.year
        ORDER BY s.name, p.year DESC
    """)
    class10_coverage = cur.fetchall()
    print("\n=== CLASS 10 SUBJECT/YEAR COVERAGE ===")
    for row in class10_coverage[:30]:
        print(f"  {row['subject_name']} ({row['year']}): {row['cnt']} papers")

conn.close()
