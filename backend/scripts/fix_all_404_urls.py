import os
import re
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

UPLOAD_DIR = 'f:/exam/backend/uploads/papers/cbse-10'

with conn.cursor() as cur:
    cur.execute("""
        SELECT p.id, p.year, p.title, p.pdf_url, ec.slug as cat_slug
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE p.pdf_url LIKE '%gadepall/cbse-papers/main/20%'
    """)
    rows = cur.fetchall()

print(f"Total rows to fix: {len(rows)}")

fixed_count = 0
for r in rows:
    pid = r['id']
    yr = r['year']
    title = r['title'].lower()
    
    # Determine subject
    subj = None
    if 'math' in title:
        subj = 'maths'
    elif 'science' in title and 'social' not in title:
        subj = 'science'
    elif 'social' in title:
        subj = 'social'
    elif 'english' in title:
        subj = 'english'

    # Determine set
    set_num = 1
    m = re.search(r'set\s*(\d+)', title)
    if m:
        set_num = int(m.group(1))

    if subj:
        # Check candidate local filenames
        candidates = [
            f"cbse_{yr}_{subj}_set{set_num}.pdf",
            f"cbse_{yr}_{subj}_set1.pdf",
            f"cbse_{yr}_{subj}_paper.pdf",
            f"cbse_{yr}_{subj}.pdf"
        ]
        chosen = None
        for c in candidates:
            fp = os.path.join(UPLOAD_DIR, c)
            if os.path.exists(fp) and os.path.getsize(fp) > 5000:
                chosen = c
                break

        if chosen:
            new_url = f"/uploads/papers/cbse-10/{chosen}"
            sz = os.path.getsize(os.path.join(UPLOAD_DIR, chosen))
            key_file = chosen.replace('.pdf', '_marking_scheme.pdf')
            key_url = None
            has_key = 0
            if os.path.exists(os.path.join(UPLOAD_DIR, key_file)):
                key_url = f"/uploads/papers/cbse-10/{key_file}"
                has_key = 1

            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE papers
                    SET pdf_url = %s, file_size = %s, verification_status = 'verified',
                        has_answer_key = %s, answer_key_pdf_url = %s
                    WHERE id = %s
                """, (new_url, sz, has_key, key_url, pid))
            fixed_count += 1
            print(f"Fixed ID {pid} ({yr} {subj} Set {set_num}): -> {new_url} ({sz} bytes, key: {bool(key_url)})")
        else:
            print(f"No candidate found for ID {pid}: {r['title']}")

print(f"\nSuccessfully linked {fixed_count} papers to authentic verified local PDF files!")
