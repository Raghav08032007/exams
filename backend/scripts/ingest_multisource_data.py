import os
import sys
import json
import urllib.request
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

UPLOAD_DIR = 'f:/exam/backend/uploads/papers'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 5000:
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read()
            if len(content) > 1000 and content.startswith(b'%PDF'):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        pass
    return False

def get_or_create_subject(name, code=None):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM subjects WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            return row['id']
        cur.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
        return cur.lastrowid

# ── 1. Ingest AIT & Arabic from boards10.github.io ────────────────────────────
print("=== 1. Ingesting AIT and Arabic from boards10.github.io ===")
with conn.cursor() as cur:
    cur.execute("SELECT id FROM exam_categories WHERE slug = 'cbse-10'")
    c10_cat = cur.fetchone()['id']

ait_subj_id = get_or_create_subject("Information Technology / AI", "417")
arabic_subj_id = get_or_create_subject("Arabic", "016")

try:
    meta_url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/final_meta.json"
    req = urllib.request.Request(meta_url, headers={'User-Agent': 'ExamVault-Bot'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        meta_data = json.loads(resp.read().decode('utf-8'))
        
        # AIT
        ait_count = 0
        for item in meta_data.get('ait', []):
            fpath = item.get('file')
            yr = item.get('year')
            raw_url = f"https://raw.githubusercontent.com/boards10/boards10.github.io/main/{fpath}"
            fname = os.path.basename(fpath)
            target = os.path.join(UPLOAD_DIR, 'cbse-10', f"ait_{fname}")
            if download_file(raw_url, target):
                sz = os.path.getsize(target)
                web_url = f"/uploads/papers/cbse-10/ait_{fname}"
                title = f"CBSE Class 10 {yr} — Information Technology / AI Official Question Paper"
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND year = %s AND title = %s", (c10_cat, yr, title))
                    if not cur.fetchone():
                        cur.execute("""
                            INSERT INTO papers (
                                exam_category_id, year, title, language, pdf_url, file_size,
                                source_url, source_name, paper_type, verification_status
                            ) VALUES (%s, %s, %s, 'English', %s, %s, %s, 'boards10.github.io', 'original', 'verified')
                        """, (c10_cat, yr, title, web_url, sz, raw_url))
                        pid = cur.lastrowid
                        cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (pid, ait_subj_id))
                        ait_count += 1

        print(f"Added {ait_count} verified Class 10 IT/AI papers!")

        # Arabic
        ar_count = 0
        for item in meta_data.get('arabic', []):
            fpath = item.get('file')
            yr = item.get('year')
            raw_url = f"https://raw.githubusercontent.com/boards10/boards10.github.io/main/{fpath}"
            fname = os.path.basename(fpath)
            target = os.path.join(UPLOAD_DIR, 'cbse-10', f"arabic_{fname}")
            if download_file(raw_url, target):
                sz = os.path.getsize(target)
                web_url = f"/uploads/papers/cbse-10/arabic_{fname}"
                title = f"CBSE Class 10 {yr} — Arabic Official Question Paper"
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND year = %s AND title = %s", (c10_cat, yr, title))
                    if not cur.fetchone():
                        cur.execute("""
                            INSERT INTO papers (
                                exam_category_id, year, title, language, pdf_url, file_size,
                                source_url, source_name, paper_type, verification_status
                            ) VALUES (%s, %s, %s, 'Arabic', %s, %s, %s, 'boards10.github.io', 'original', 'verified')
                        """, (c10_cat, yr, title, web_url, sz, raw_url))
                        pid = cur.lastrowid
                        cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (pid, arabic_subj_id))
                        ar_count += 1
        print(f"Added {ar_count} verified Class 10 Arabic papers!")

except Exception as e:
    print(f"Error fetching boards10 meta: {e}")

# ── 2. Ingest State Boards from Shabber10/ALL-PYQ-Papers ────────────────────────
print("\n=== 2. Ingesting State Boards from Shabber10/ALL-PYQ-Papers ===")
def get_github_tree(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return []

board_slug_map = {
    "Maharashtra": ("maharashtra-board", "Maharashtra State Board (MSBSHSE)"),
    "Andhra_Pradesh": ("ap-board", "Andhra Pradesh Board (BSEAP)"),
    "West_Bengal": ("wb-board", "West Bengal Board (WBBSE)"),
    "Kerala": ("kerala-board", "Kerala Board (KBPE)"),
    "Uttar_Pradesh": ("up-board", "Uttar Pradesh Board (UPMSP)"),
    "Bihar": ("bihar-board", "Bihar Board (BSEB)"),
    "Telangana": ("telangana-board", "Telangana Board (BSE)"),
    "Rajasthan": ("rajasthan-board", "Rajasthan Board (RBSE)")
}

total_state_added = 0
for bname, (cat_slug, display_name) in board_slug_map.items():
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM exam_categories WHERE slug = %s", (cat_slug,))
        row = cur.fetchone()
        if not row:
            continue
        cat_id = row['id']

    years_tree = get_github_tree("Shabber10/ALL-PYQ-Papers", f"Boards/{bname}")
    for yitem in years_tree:
        if yitem.get('type') == 'dir' and yitem['name'].isdigit():
            yr = int(yitem['name'])
            files = get_github_tree("Shabber10/ALL-PYQ-Papers", yitem['path'])
            for f in files:
                if f.get('type') == 'file' and f['name'].lower().endswith('.pdf'):
                    fname = f['name']
                    raw_download_url = f.get('download_url')
                    if not raw_download_url:
                        raw_download_url = f"https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/{bname}/{yr}/{fname}"

                    # Clean subject name from filename
                    clean_name = fname.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
                    sub_guess = "General"
                    for s_test in ["mathematics", "maths", "math", "physics", "chemistry", "biology", "science", "social", "english", "hindi"]:
                        if s_test in clean_name.lower():
                            sub_guess = s_test.capitalize()
                            if sub_guess == 'Math' or sub_guess == 'Maths':
                                sub_guess = 'Mathematics'
                            break

                    subj_id = get_or_create_subject(sub_guess)
                    title = f"{display_name} {yr} — {clean_name}"
                    
                    # Store with raw URL or download
                    target = os.path.join(UPLOAD_DIR, cat_slug, fname)
                    web_url = raw_download_url
                    fsize = f.get('size', 100000)
                    if download_file(raw_download_url, target):
                        fsize = os.path.getsize(target)
                        web_url = f"/uploads/papers/{cat_slug}/{fname}"

                    with conn.cursor() as cur:
                        cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND title = %s", (cat_id, title))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO papers (
                                    exam_category_id, year, title, language, pdf_url, file_size,
                                    source_url, source_name, paper_type, verification_status
                                ) VALUES (%s, %s, %s, 'English', %s, %s, %s, 'Shabber10/ALL-PYQ-Papers', 'original', 'verified')
                            """, (cat_id, yr, title, web_url, fsize, raw_download_url))
                            pid = cur.lastrowid
                            cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (pid, subj_id))
                            total_state_added += 1

print(f"\nTotal state board papers ingested: {total_state_added}!")
