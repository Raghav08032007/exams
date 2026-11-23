import os
import pymysql
import urllib.request
import urllib.parse
import concurrent.futures
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
        WHERE p.exam_category_id = 69 AND (p.pdf_url LIKE 'http://%' OR p.pdf_url LIKE 'https://%')
    """)
    remote_papers = cur.fetchall()

print(f"Total remote papers in CBSE Class 12 to download: {len(remote_papers)}")

dest_dir = os.path.abspath('f:/exam/backend/uploads/papers/cbse-12')
os.makedirs(dest_dir, exist_ok=True)

success_updates = []
failed_downloads = []

def download_and_save(p):
    pid = p['id']
    url = p['pdf_url']
    parsed = urllib.parse.urlsplit(url)
    unquoted_path = urllib.parse.unquote(parsed.path)
    clean_path = urllib.parse.quote(unquoted_path)
    clean_query = urllib.parse.quote(urllib.parse.unquote(parsed.query), safe='=&')
    clean_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, clean_path, clean_query, parsed.fragment))

    base_name = os.path.basename(unquoted_path)
    safe_base = "".join(c if (c.isalnum() or c in "._-") else "_" for c in base_name)
    if not safe_base.endswith('.pdf'):
        safe_base = f"paper_{pid}_{safe_base}.pdf"
    else:
        safe_base = f"{pid}_{safe_base}"
    
    dest_path = os.path.join(dest_dir, safe_base)
    rel_url = f"/uploads/papers/cbse-12/{safe_base}"

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return (pid, 'EXISTS', rel_url, os.path.getsize(dest_path))

    req = urllib.request.Request(
        clean_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
            if data and (b'%PDF' in data[:1024]):
                with open(dest_path, 'wb') as f:
                    f.write(data)
                return (pid, 'DOWNLOADED', rel_url, len(data))
            else:
                return (pid, 'INVALID_PDF', clean_url, len(data) if data else 0)
    except Exception as e:
        return (pid, 'ERROR', clean_url, str(e))

print("Starting parallel download with 25 workers...")
with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
    futures = {executor.submit(download_and_save, p): p for p in remote_papers}
    for future in concurrent.futures.as_completed(futures):
        res = future.result()
        if res[1] in ('EXISTS', 'DOWNLOADED'):
            success_updates.append((res[2], res[0]))
        else:
            failed_downloads.append(res)

print(f"\nResults: {len(success_updates)} successful, {len(failed_downloads)} failed.")

if success_updates:
    print(f"Updating {len(success_updates)} database records to local /uploads/ URLs...")
    with conn.cursor() as cur:
        cur.executemany("UPDATE papers SET pdf_url = %s, file_size = NULL WHERE id = %s", success_updates)
    conn.commit()
    print("Database updated successfully!")

if failed_downloads:
    print(f"\nExamining {len(failed_downloads)} failed downloads:")
    for f in failed_downloads[:20]:
        print(" ", f)
