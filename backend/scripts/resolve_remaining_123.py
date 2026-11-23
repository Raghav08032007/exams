import os
import pymysql
import re
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
        WHERE ec.slug = 'cbse-10' AND (p.pdf_url LIKE 'http://%' OR p.pdf_url LIKE 'https://%')
    """)
    remaining = cur.fetchall()

print(f"Checking {len(remaining)} remaining remote papers...")
upload_dir = 'f:/exam/backend/uploads/papers/cbse-10'
local_files = os.listdir(upload_dir)

duplicates_to_delete = []
relink_updates = []
unmatched = []

for r in remaining:
    norm_title = re.sub(r'[\s_\-\(\)\.]+', ' ', r['title'].lower()).strip()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, pdf_url
            FROM papers
            WHERE exam_category_id = 64 AND pdf_url LIKE '/uploads/%%' AND year = %s AND id != %s
        """, (r['year'], r['id']))
        candidates = cur.fetchall()
    
    found_twin = None
    for c in candidates:
        norm_c = re.sub(r'[\s_\-\(\)\.]+', ' ', c['title'].lower()).strip()
        if norm_title == norm_c or norm_title.replace(' ', '') == norm_c.replace(' ', ''):
            found_twin = c
            break
    
    if found_twin:
        print(f"Duplicate found: ID {r['id']} -> twin {found_twin['id']} ({found_twin['title']})")
        duplicates_to_delete.append(r['id'])
    else:
        # Check if local file exists by partial name
        base = os.path.basename(r['pdf_url']).replace('%20', ' ')
        core_name = re.sub(r'[\s_\-\(\)\.]+', '', base.lower().replace('.pdf', ''))
        found_file = None
        for lf in local_files:
            core_lf = re.sub(r'[\s_\-\(\)\.]+', '', lf.lower().replace('.pdf', ''))
            if core_name in core_lf or core_lf in core_name:
                found_file = lf
                break
        if found_file:
            print(f"Relink: ID {r['id']} -> /uploads/papers/cbse-10/{found_file}")
            relink_updates.append((f"/uploads/papers/cbse-10/{found_file}", r['id']))
        else:
            unmatched.append(r)

print(f"\nDuplicates to delete: {len(duplicates_to_delete)}")
print(f"Relinks to local files: {len(relink_updates)}")
print(f"Still unmatched: {len(unmatched)}")

if duplicates_to_delete:
    fmt = ",".join(["%s"] * len(duplicates_to_delete))
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM paper_subjects WHERE paper_id IN ({fmt})", duplicates_to_delete)
        cur.execute(f"DELETE FROM user_notes WHERE paper_id IN ({fmt})", duplicates_to_delete)
        cur.execute(f"DELETE FROM practice_attempts WHERE paper_id IN ({fmt})", duplicates_to_delete)
        cur.execute(f"DELETE FROM bookmarks WHERE paper_id IN ({fmt})", duplicates_to_delete)
        cur.execute(f"DELETE FROM papers WHERE id IN ({fmt})", duplicates_to_delete)
    conn.commit()
    print("Deleted all duplicate records from database!")

if relink_updates:
    with conn.cursor() as cur:
        cur.executemany("UPDATE papers SET pdf_url = %s WHERE id = %s", relink_updates)
    conn.commit()
    print("Relinked remaining papers to authentic local files!")

if unmatched:
    print(f"\nExamining {len(unmatched)} unmatched papers:")
    for u in unmatched[:10]:
        print(" ", u['id'], u['year'], u['title'], u['pdf_url'])
