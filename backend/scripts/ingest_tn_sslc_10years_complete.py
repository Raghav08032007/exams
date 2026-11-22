import urllib.request
import re
import ssl
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
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_url = "https://www.educationobserver.com/forum/"

# Subject mapping
SUBJECT_MAP = {
    'tamil': 147,
    'english': 815,
    'math': 48,
    'maths': 48,
    'mathematics': 48,
    'science': 28,
    'social': 90,
}

# The target categories:
# 67: TN SSLC 10th (under Class 10)
# 2626: Tamil Nadu State Board (DGE) (under State Boards)
TARGET_CATEGORIES = [67, 2626]

# Threads configuration
YEAR_THREADS = {
    2024: [
        "https://www.educationobserver.com/forum/showthread.php?tid=29233", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=29236", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=29240", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=29379", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=31632", # Social
    ],
    2023: [
        "https://www.educationobserver.com/forum/showthread.php?tid=28098", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=28108", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=28116", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=28127", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=28128", # Social
    ],
    2022: [
        "https://www.educationobserver.com/forum/showthread.php?tid=27586", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=27585", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=27589", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=27587", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=27588", # Social
    ],
    2021: [
        "https://www.educationobserver.com/forum/showthread.php?tid=24295", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=24297", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=24293", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=24296", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=24298", # Social
    ],
    2020: [
        "https://www.educationobserver.com/forum/showthread.php?tid=24295",
        "https://www.educationobserver.com/forum/showthread.php?tid=24297",
        "https://www.educationobserver.com/forum/showthread.php?tid=24293",
        "https://www.educationobserver.com/forum/showthread.php?tid=24296",
        "https://www.educationobserver.com/forum/showthread.php?tid=24298",
    ],
    2019: [
        "https://www.educationobserver.com/forum/showthread.php?tid=23265",
    ],
    2018: [
        "https://www.educationobserver.com/forum/showthread.php?tid=21844",
    ],
    2017: [
        "https://www.educationobserver.com/forum/showthread.php?tid=21102",
    ],
    2016: [
        "https://www.educationobserver.com/forum/showthread.php?tid=21110",
    ],
    2015: [
        "https://www.educationobserver.com/forum/showthread.php?tid=18002",
    ]
}

def detect_subject(text):
    t = text.lower()
    if 'social' in t:
        return 'Social Science', 90
    if 'science' in t:
        return 'Science', 28
    if 'math' in t:
        return 'Mathematics', 48
    if 'english' in t:
        return 'English', 815
    if 'tamil' in t:
        return 'Tamil', 147
    return None, None

def ingest():
    total_added = 0
    cur = conn.cursor()

    for year, urls in YEAR_THREADS.items():
        print(f"\n>>> Processing Year {year}...")
        for url in urls:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            try:
                with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"  Failed to fetch {url}: {e}")
                continue

            # Find all attachments
            atts = re.findall(r'href=[\'"]([^\'"]*attachment\.php\?aid=(\d+))[^\'"]*[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
            
            # Group into Question Papers vs Answer Keys
            q_papers = []
            a_keys = {}

            for href, aid, raw_title in atts:
                clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
                full_href = href if href.startswith('http') else base_url + href
                sub_name, sub_id = detect_subject(clean_title)
                if not sub_name:
                    continue

                is_key = any(k in clean_title.lower() for k in ['answer key', 'key answer', 'solution', 'keys'])
                if is_key:
                    # store answer key for this subject
                    a_keys.setdefault(sub_id, []).append((clean_title, full_href))
                else:
                    q_papers.append((clean_title, full_href, sub_name, sub_id))

            # If no explicit question paper was marked (some titles combine both), treat all non-keys or all items
            if not q_papers and a_keys:
                for sub_id, keys in a_keys.items():
                    for kt, kh in keys:
                        sub_name = [k for k, v in SUBJECT_MAP.items() if v == sub_id][0].capitalize()
                        q_papers.append((kt, kh, sub_name, sub_id))

            for title, pdf_url, sub_name, sub_id in q_papers:
                # Find matching answer key if available
                key_url = None
                if sub_id in a_keys and a_keys[sub_id]:
                    key_url = a_keys[sub_id][0][1]

                # Format clean official title
                session = "March Public Exam" if year != 2021 and year != 2020 else "Revision Public Exam"
                if "september" in title.lower():
                    session = "September Supplementary"
                
                clean_title = f"Tamil Nadu SSLC Class 10 {sub_name} Question Paper {year} ({session})"
                if "paper 1" in title.lower() or "paper i" in title.lower() or "tamil 1" in title.lower():
                    clean_title += " - Paper I"
                elif "paper 2" in title.lower() or "paper ii" in title.lower() or "tamil ii" in title.lower():
                    clean_title += " - Paper II"
                elif "tamil med" in title.lower() or "tm" in title.lower():
                    clean_title += " (Tamil Medium)"
                elif "eng med" in title.lower() or "em" in title.lower():
                    clean_title += " (English Medium)"

                for cat_id in TARGET_CATEGORIES:
                    # Check if already exists
                    cur.execute(
                        "SELECT id FROM papers WHERE exam_category_id = %s AND pdf_url = %s",
                        (cat_id, pdf_url)
                    )
                    existing = cur.fetchone()
                    if existing:
                        continue

                    # Insert paper
                    cur.execute("""
                        INSERT INTO papers (
                            exam_category_id, year, session, title, language, pdf_url, 
                            has_answer_key, answer_key_pdf_url, verification_status,
                            source_url, source_name, paper_type
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, 
                            %s, %s, 'verified',
                            %s, 'Tamil Nadu Directorate of Government Examinations (DGE)', 'Official Public Exam'
                        )
                    """, (
                        cat_id, year, session, clean_title, 
                        'Tamil & English' if sub_name != 'Tamil' and sub_name != 'English' else sub_name,
                        pdf_url,
                        1 if key_url else 0,
                        key_url,
                        url
                    ))
                    paper_id = cur.lastrowid
                    
                    # Link to subject
                    cur.execute("""
                        INSERT IGNORE INTO paper_subjects (paper_id, subject_id)
                        VALUES (%s, %s)
                    """, (paper_id, sub_id))

                    total_added += 1

        print(f"  Cumulative added so far: {total_added}")

    conn.close()
    print(f"\nDone! Ingested {total_added} total TN SSLC papers across both categories!")

if __name__ == '__main__':
    ingest()
