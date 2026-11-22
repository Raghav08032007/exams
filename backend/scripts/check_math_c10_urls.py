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
        SELECT p.id, p.year, p.session, p.title, p.pdf_url, p.has_answer_key, p.answer_key_pdf_url
        FROM papers p
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        WHERE (p.exam_category_id = 64 OR p.exam_category_id = 67)
          AND s.name = 'Mathematics'
        ORDER BY p.year DESC, p.id ASC
    """)
    rows = cur.fetchall()
    print(f"Total Class 10 Math Papers: {len(rows)}")
    
    # Check sample URLs by year
    years_seen = {}
    for r in rows:
        yr = r['year']
        if yr not in years_seen:
            years_seen[yr] = []
        years_seen[yr].append(r)

    for yr in sorted(years_seen.keys(), reverse=True):
        papers_yr = years_seen[yr]
        print(f"\n--- Year {yr} ({len(papers_yr)} papers) ---")
        for p in papers_yr[:3]:
            print(f"  id: {p['id']}, title: {p['title'][:55]}, url: {p['pdf_url']}")

conn.close()
