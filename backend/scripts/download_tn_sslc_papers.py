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

upload_dir = 'f:/exam/backend/uploads/papers/tn-sslc'
os.makedirs(upload_dir, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with conn.cursor() as cur:
    cur.execute("""
        SELECT p.id, p.year, s.name as sub, p.title, p.pdf_url
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        LEFT JOIN paper_subjects ps ON p.id = ps.paper_id
        LEFT JOIN subjects s ON ps.subject_id = s.id
        WHERE ec.slug = 'tn-sslc' AND p.pdf_url LIKE 'https://www.educationobserver.com/%'
    """)
    rows = cur.fetchall()

print(f"Found {len(rows)} TN SSLC papers from educationobserver to download & verify...")

success = 0
failed = 0

for r in rows:
    pid = r['id']
    url = r['pdf_url']
    sub = (r['sub'] or 'general').lower().replace(' ', '_')
    yr = r['year']
    fn = f"tn_sslc_{yr}_{sub}_{pid}.pdf"
    fp = os.path.join(upload_dir, fn)
    rel_path = f"/uploads/papers/tn-sslc/{fn}"

    if os.path.exists(fp) and os.path.getsize(fp) > 5000:
        sz = os.path.getsize(fp)
        with conn.cursor() as cur:
            cur.execute("UPDATE papers SET pdf_url = %s, file_size = %s, verification_status = 'verified' WHERE id = %s", (rel_path, sz, pid))
        conn.commit()
        success += 1
        continue

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            data = resp.read()
            if len(data) > 5000 and data[:4] == b'%PDF':
                with open(fp, 'wb') as f:
                    f.write(data)
                sz = len(data)
                with conn.cursor() as cur:
                    cur.execute("UPDATE papers SET pdf_url = %s, file_size = %s, verification_status = 'verified' WHERE id = %s", (rel_path, sz, pid))
                conn.commit()
                success += 1
                print(f"  [OK] Saved {fn} ({sz} bytes)")
            else:
                failed += 1
                print(f"  [WARN] Not valid PDF: {url}")
    except Exception as e:
        failed += 1
        print(f"  [ERR] {pid} ({url}): {e}")

print(f"\nTN SSLC Download complete: {success} verified & saved locally, {failed} failed")
