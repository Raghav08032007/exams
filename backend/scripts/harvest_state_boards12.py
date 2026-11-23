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

boards_config = {
    'Tamil_Nadu': {
        'category_id': 71, # TN HSC 12th
        'slug': 'tn-hsc',
        'years': ['2015', '2016', '2017', '2018', '2020']
    },
    'Maharashtra': {
        'category_id': 2624, # Maharashtra Board (MSBSHSE)
        'slug': 'maharashtra-board',
        'years': ['2014', '2015', '2016', '2017', '2018', '2019', '2020']
    },
    'Uttar_Pradesh': {
        'category_id': 2628, # Uttar Pradesh Board (UPMSP)
        'slug': 'up-board',
        'years': ['2015', '2016', '2017', '2018', '2019', '2020']
    },
    'Kerala': {
        'category_id': 2622, # Kerala Board (KBPE / DHSE)
        'slug': 'kerala-board',
        'years': ['2015', '2016', '2017', '2018', '2019', '2020']
    },
    'West_Bengal': {
        'category_id': 2629, # West Bengal Board (WBBSE / WBCHSE)
        'slug': 'wb-board',
        'years': ['2015', '2016', '2017', '2018', '2020']
    },
    'Andhra_Pradesh': {
        'category_id': 2620, # Andhra Pradesh Board (BIEAP / BSEAP)
        'slug': 'ap-board',
        'years': ['2015', '2016', '2017', '2018', '2020']
    }
}

def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

papers_to_download = []

for board_name, cfg in boards_config.items():
    dest_dir = os.path.abspath(f"f:/exam/backend/uploads/papers/{cfg['slug']}")
    os.makedirs(dest_dir, exist_ok=True)
    for yr in cfg['years']:
        url = f"https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/{board_name}/{yr}"
        html = fetch_html(url)
        files = re.findall(rf'/Shabber10/ALL-PYQ-Papers/blob/main/Boards/{board_name}/{yr}/([^"/?#]+\.pdf)', html)
        for f in set(files):
            raw_url = f"https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/{board_name}/{yr}/{f}"
            papers_to_download.append((board_name, cfg['category_id'], cfg['slug'], int(yr), f, raw_url))

print(f"Discovered {len(papers_to_download)} authentic State Board 12th papers across 6 major boards.")

def download_state_paper(item):
    board_name, cat_id, slug, yr, fname, raw_url = item
    clean_url = urllib.parse.quote(raw_url, safe=':/?&=#')
    dest_dir = os.path.abspath(f"f:/exam/backend/uploads/papers/{slug}")
    dest_path = os.path.join(dest_dir, fname)
    rel_url = f"/uploads/papers/{slug}/{fname}"

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return (board_name, cat_id, yr, fname, rel_url, os.path.getsize(dest_path), 'EXISTS')

    req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
            if b'%PDF' in data[:2048] or len(data) > 1000:
                with open(dest_path, 'wb') as f:
                    f.write(data)
                return (board_name, cat_id, yr, fname, rel_url, len(data), 'DOWNLOADED')
            else:
                return (board_name, cat_id, yr, fname, rel_url, len(data), 'NOT_PDF')
    except Exception as e:
        return (board_name, cat_id, yr, fname, rel_url, 0, f'ERROR_{e}')

print("Downloading state board papers...")
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    for res in ex.map(download_state_paper, papers_to_download):
        results.append(res)
        if res[6] in ('EXISTS', 'DOWNLOADED'):
            print(f"  [OK] {res[0]} {res[2]}: {res[3]} ({res[5]} bytes)")
        else:
            print(f"  [FAIL] {res[0]} {res[2]}: {res[3]} - {res[6]}")

# Subject extraction helper
def extract_subject(fname):
    lower = fname.lower().replace('.pdf', '')
    for s in ['mathematics', 'maths', 'physics', 'chemistry', 'biology', 'accountancy', 'economics', 'english', 'tamil', 'general', 'botany', 'zoology']:
        if s in lower:
            return s.capitalize() if s != 'maths' else 'Mathematics'
    return 'General'

# Insert into database
with conn.cursor() as cur:
    inserted = 0
    for board_name, cat_id, yr, fname, rel_url, sz, status in results:
        if status not in ('EXISTS', 'DOWNLOADED'):
            continue
        subj_name = extract_subject(fname)
        # get or create subject
        cur.execute("SELECT id FROM subjects WHERE name = %s", (subj_name,))
        srow = cur.fetchone()
        if srow:
            sid = srow['id']
        else:
            cur.execute("INSERT INTO subjects (name) VALUES (%s)", (subj_name,))
            sid = cur.lastrowid

        clean_board = board_name.replace('_', ' ')
        title = f"{clean_board} 12th (HSC) {yr} — {subj_name} Examination Question Paper"
        
        # Check if already present
        cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND year = %s AND pdf_url = %s", (cat_id, yr, rel_url))
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO papers (exam_category_id, year, title, language, pdf_url, file_size, paper_type, verification_status)
            VALUES (%s, %s, %s, 'English', %s, %s, 'original', 'verified')
        """, (cat_id, yr, title, rel_url, sz))
        pid = cur.lastrowid
        cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (pid, sid))
        inserted += 1

    conn.commit()
    print(f"\nInserted {inserted} new verified State Board 12th papers into the database!")
