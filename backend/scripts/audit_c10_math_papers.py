import os
import pymysql
import urllib.request
import ssl
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

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with conn.cursor() as cur:
    cur.execute("""
        SELECT p.id, p.year, p.title, p.pdf_url, p.has_answer_key, p.answer_key_pdf_url, ec.slug as cat_slug
        FROM papers p
        JOIN paper_subjects ps ON p.id = ps.paper_id
        JOIN subjects s ON ps.subject_id = s.id
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE ec.slug IN ('cbse-10', 'tn-sslc')
          AND s.name = 'Mathematics'
        ORDER BY p.year DESC, p.id ASC
    """)
    papers = cur.fetchall()
    print(f"Total Class 10 Math papers in CBSE & TN SSLC: {len(papers)}")

    # Group by year
    by_year = {}
    for p in papers:
        by_year.setdefault(p['year'], []).append(p)

    for yr in sorted(by_year.keys(), reverse=True):
        plist = by_year[yr]
        print(f"\n=== Year {yr} ({len(plist)} papers) ===")
        for p in plist[:4]:
            url = p['pdf_url']
            status = "UNKNOWN"
            if url.startswith('/uploads/'):
                local_path = os.path.join('f:/exam/backend', url.lstrip('/'))
                status = f"LOCAL ({os.path.getsize(local_path)} bytes)" if os.path.exists(local_path) else "MISSING LOCAL"
            elif url.startswith('http'):
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                        status = f"REMOTE 200 ({resp.headers.get('Content-Length', 'chunked')} bytes)"
                except Exception as e:
                    status = f"REMOTE ERROR: {e}"
            print(f"  id: {p['id']} [{p['cat_slug']}] {p['title'][:45]} -> {status}")

conn.close()
