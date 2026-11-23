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
        SELECT p.id, p.exam_category_id, ec.slug, p.year, p.title, p.pdf_url
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE p.pdf_url LIKE 'http://%' OR p.pdf_url LIKE 'https://%'
    """)
    remote_papers = cur.fetchall()

print(f"Total remote papers remaining across ALL categories: {len(remote_papers)}")

to_update = []
to_delete = []

for p in remote_papers:
    pid = p['id']
    url = p['pdf_url']
    cat_id = p['exam_category_id']
    slug = p['slug']
    fname = os.path.basename(urllib.parse.urlsplit(url).path)
    
    # Check if this exact file is already in uploads
    dest_path = os.path.abspath(f"f:/exam/backend/uploads/papers/{slug}/{fname}")
    rel_url = f"/uploads/papers/{slug}/{fname}"
    
    # Check if another record already has this exact rel_url
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND pdf_url = %s AND id != %s", (cat_id, rel_url, pid))
        dup = cur.fetchone()
    
    if dup:
        to_delete.append(pid)
    elif os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        to_update.append((rel_url, pid))
    else:
        # Download it
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                if len(data) > 1000:
                    with open(dest_path, 'wb') as f:
                        f.write(data)
                    to_update.append((rel_url, pid))
        except Exception as e:
            print(f"Download error {pid} {url}: {e}")

print(f"To update to local: {len(to_update)}")
print(f"To delete duplicates: {len(to_delete)}")

if to_delete:
    fmt = ",".join(["%s"] * len(to_delete))
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM paper_subjects WHERE paper_id IN ({fmt})", to_delete)
        cur.execute(f"DELETE FROM user_notes WHERE paper_id IN ({fmt})", to_delete)
        cur.execute(f"DELETE FROM practice_attempts WHERE paper_id IN ({fmt})", to_delete)
        cur.execute(f"DELETE FROM bookmarks WHERE paper_id IN ({fmt})", to_delete)
        cur.execute(f"DELETE FROM papers WHERE id IN ({fmt})", to_delete)
    conn.commit()
    print("Deleted duplicate records!")

if to_update:
    with conn.cursor() as cur:
        cur.executemany("UPDATE papers SET pdf_url = %s WHERE id = %s", to_update)
    conn.commit()
    print("Updated papers to local URLs!")
