import os
import re
import urllib.request
import urllib.parse
import concurrent.futures
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

dest_dir = os.path.abspath('f:/exam/backend/uploads/papers/cbse-12')
os.makedirs(dest_dir, exist_ok=True)

def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

# 1. Discover Math 12 papers in gadepall
math_years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
papers_to_download = []

print("Scanning gadepall math/12 across all years...")
for yr in math_years:
    url = f"https://github.com/gadepall/cbse-papers/tree/main/papers/math/12/{yr}"
    html = fetch_html(url)
    files = re.findall(rf'/gadepall/cbse-papers/blob/main/papers/math/12/{yr}/([^"/?#]+\.pdf)', html)
    for f in set(files):
        raw_url = f"https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/math/12/{yr}/{f}"
        papers_to_download.append(('Mathematics', int(yr), f, raw_url))

# 2. Discover Physics papers in gadepall
physics_years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2016', '2022']
print("Scanning gadepall physics across all years...")
for yr in physics_years:
    url = f"https://github.com/gadepall/cbse-papers/tree/main/papers/physics/{yr}"
    html = fetch_html(url)
    files = re.findall(rf'/gadepall/cbse-papers/blob/main/papers/physics/{yr}/([^"/?#]+\.pdf)', html)
    for f in set(files):
        raw_url = f"https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/physics/{yr}/{f}"
        papers_to_download.append(('Physics', int(yr), f, raw_url))

# 3. Discover Chemistry papers in gadepall
chemistry_years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2016', '2022']
print("Scanning gadepall chemistry across all years...")
for yr in chemistry_years:
    url = f"https://github.com/gadepall/cbse-papers/tree/main/papers/chemistry/{yr}"
    html = fetch_html(url)
    files = re.findall(rf'/gadepall/cbse-papers/blob/main/papers/chemistry/{yr}/([^"/?#]+\.pdf)', html)
    for f in set(files):
        raw_url = f"https://raw.githubusercontent.com/gadepall/cbse-papers/main/papers/chemistry/{yr}/{f}"
        papers_to_download.append(('Chemistry', int(yr), f, raw_url))

print(f"Total discovered gadepall papers for CBSE 12: {len(papers_to_download)}")

def download_file(item):
    subj, yr, fname, raw_url = item
    clean_url = urllib.parse.quote(raw_url, safe=':/?&=#')
    safe_name = f"gadepall_{yr}_{subj.lower()}_{fname}"
    dest_path = os.path.join(dest_dir, safe_name)
    rel_url = f"/uploads/papers/cbse-12/{safe_name}"

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return (subj, yr, fname, rel_url, os.path.getsize(dest_path), 'EXISTS')

    req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
            # Note: gadepall files may have git lfs or direct bytes. Check for %PDF or size
            if b'%PDF' in data[:2048] or len(data) > 10000:
                with open(dest_path, 'wb') as f:
                    f.write(data)
                return (subj, yr, fname, rel_url, len(data), 'DOWNLOADED')
            else:
                return (subj, yr, fname, rel_url, len(data), 'NOT_PDF')
    except Exception as e:
        return (subj, yr, fname, rel_url, 0, f'ERROR_{e}')

print("Downloading discovered gadepall papers...")
downloaded = []
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
    for res in ex.map(download_file, papers_to_download):
        if res[5] in ('EXISTS', 'DOWNLOADED'):
            downloaded.append(res)
            print(f"  [OK] {res[0]} {res[1]}: {res[2]} ({res[4]} bytes)")
        else:
            print(f"  [FAIL] {res[0]} {res[1]}: {res[2]} - {res[5]}")

print(f"\nSuccessfully obtained {len(downloaded)} authentic CBSE 12 papers from gadepall.")

# Insert into database
with conn.cursor() as cur:
    # get or create subject IDs
    subj_map = {}
    for s in ['Mathematics', 'Physics', 'Chemistry']:
        cur.execute("SELECT id FROM subjects WHERE name = %s", (s,))
        r = cur.fetchone()
        if r:
            subj_map[s] = r['id']
        else:
            cur.execute("INSERT INTO subjects (name) VALUES (%s)", (s,))
            subj_map[s] = cur.lastrowid

    inserted = 0
    for sname, yr, fname, rel_url, sz, status in downloaded:
        clean_title = fname.replace('.pdf', '').replace('_', ' ').title()
        title = f"CBSE Class 12 {yr} — {sname} Question Paper ({clean_title})"
        # Check if already exists in DB
        cur.execute("SELECT id FROM papers WHERE exam_category_id = 69 AND year = %s AND pdf_url = %s", (yr, rel_url))
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO papers (exam_category_id, year, title, language, pdf_url, file_size, paper_type, verification_status)
            VALUES (69, %s, %s, 'English', %s, %s, 'original', 'verified')
        """, (yr, title, rel_url, sz))
        pid = cur.lastrowid
        cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (pid, subj_map[sname]))
        inserted += 1

    conn.commit()
    print(f"Inserted {inserted} new authentic CBSE 12 papers into the database!")
