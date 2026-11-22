import os
import sys
import json
import re
import urllib.request
import urllib.parse
import pymysql.cursors

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "261008")
DB_NAME = os.getenv("MYSQL_DB", "examvault")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_subject_name(raw: str) -> str:
    s = raw.replace(".pdf", "").replace("-", " ").replace("_", " ").strip().title()
    # Map common variations
    mapping = {
        "Maths": "Mathematics",
        "Math": "Mathematics",
        "Sci": "Science",
        "Social Sci": "Social Science",
        "Comp Sci": "Computer Science",
        "Cs": "Computer Science",
        "Ai": "Artificial Intelligence",
        "It": "Information Technology",
        "Phy": "Physics",
        "Chem": "Chemistry",
        "Bio": "Biology",
        "Econ": "Economics",
        "Eco": "Economics",
        "Pol Sci": "Polity",
        "Gs 1": "General Studies",
        "Gs 2": "General Studies",
        "Gs 3": "General Studies",
        "Gs 4": "General Studies",
        "General Studies Paper I": "General Studies",
        "General Studies Paper Ii": "CSAT",
        "Csat Paper Ii": "CSAT",
    }
    for k, v in mapping.items():
        if s.lower() == k.lower():
            return v
    return s

def get_or_create_subject(cur, name: str) -> int:
    cur.execute("SELECT id FROM subjects WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row["id"] if isinstance(row, dict) else row[0]
    
    cur.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
    return cur.lastrowid

def sync_shabber_pyqs(conn):
    print("=" * 60)
    print("Fetching GitHub tree for Shabber10/ALL-PYQ-Papers...")
    url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        tree = data.get("tree", [])

    print(f"Total entries in repo tree: {len(tree)}")
    pdf_items = [x for x in tree if x["path"].lower().endswith(".pdf")]
    print(f"Total PDF documents found: {len(pdf_items)}")

    # Category mappings:
    # Class 10 CBSE: exam_id 25, cat_id 64
    # Class 10 TN: exam_id 25, cat_id 67
    # Class 12 CBSE: exam_id 26, cat_id 69
    # Class 12 TN: exam_id 26, cat_id 71
    # UPSC Prelims: exam_id 2, cat_id 6
    # UPSC Mains: exam_id 2, cat_id 7
    # JEE Main: exam_id 3, cat_id 8
    # JEE Advanced: exam_id 3, cat_id 9
    # NEET UG: exam_id 4, cat_id 10

    # Build solution map for NEET or any other pairs
    solution_map = {}
    for item in pdf_items:
        path = item["path"]
        if "solution" in path.lower() or "answer" in path.lower() or "key" in path.lower():
            key_base = path.lower().replace("-solution.pdf", "").replace("-answer.pdf", "").replace("-key.pdf", "")
            solution_map[key_base] = f"https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/{urllib.parse.quote(path)}"

    ingested_count = 0
    updated_count = 0

    cur = conn.cursor(pymysql.cursors.DictCursor)

    for item in pdf_items:
        path = item["path"]
        raw_url = f"https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/{urllib.parse.quote(path)}"
        gh_blob_url = f"https://github.com/Shabber10/ALL-PYQ-Papers/blob/main/{urllib.parse.quote(path)}"
        file_size = item.get("size", 2500000)

        exam_id = None
        cat_id = None
        year = None
        session = None
        subject_name = "General"
        title = ""
        paper_type = "original"

        # 1. CBSE Class 10: Boards/CBSE/10/<year>/CBSE-Class-10-<year>-<subject>.pdf
        m_cbse10 = re.match(r"Boards/CBSE/10/(\d{4})/CBSE-Class-10-\d{4}-(.+)\.pdf", path, re.I)
        if m_cbse10:
            exam_id = 25
            cat_id = 64
            year = int(m_cbse10.group(1))
            raw_sub = m_cbse10.group(2)
            subject_name = clean_subject_name(raw_sub)
            title = f"CBSE Class 10 {year} — {subject_name} Question Paper"

        # 2. CBSE Class 12: Boards/CBSE/12/<year>/CBSE-Class-12-<year>-<subject>.pdf
        m_cbse12 = re.match(r"Boards/CBSE/12/(\d{4})/CBSE-Class-12-\d{4}-(.+)\.pdf", path, re.I)
        if m_cbse12:
            exam_id = 26
            cat_id = 69
            year = int(m_cbse12.group(1))
            raw_sub = m_cbse12.group(2)
            subject_name = clean_subject_name(raw_sub)
            title = f"CBSE Class 12 {year} — {subject_name} Question Paper"

        # 3. UPSC Prelims: UPSC/Civil_Services/Prelims/<year>/UPSC-CSE-Prelims-<year>-(.+)\.pdf
        m_upsc_pre = re.match(r"UPSC/Civil_Services/Prelims/(\d{4})/UPSC-CSE-Prelims-\d{4}-(.+)\.pdf", path, re.I)
        if m_upsc_pre:
            exam_id = 2
            cat_id = 6
            year = int(m_upsc_pre.group(1))
            sub_part = m_upsc_pre.group(2).lower()
            if "paper-ii" in sub_part or "csat" in sub_part:
                subject_name = "CSAT"
                title = f"UPSC Civil Services Prelims {year} — CSAT (Paper II)"
            else:
                subject_name = "General Studies"
                title = f"UPSC Civil Services Prelims {year} — General Studies (Paper I)"

        # 4. UPSC Mains: UPSC/Civil_Services/Mains/<year>/UPSC-CSE-Mains-<year>-(.+)\.pdf
        m_upsc_main = re.match(r"UPSC/Civil_Services/Mains/(\d{4})/UPSC-CSE-Mains-\d{4}-(.+)\.pdf", path, re.I)
        if m_upsc_main:
            exam_id = 2
            cat_id = 7
            year = int(m_upsc_main.group(1))
            raw_sub = m_upsc_main.group(2)
            subject_name = clean_subject_name(raw_sub)
            title = f"UPSC Civil Services Mains {year} — {subject_name}"

        # 5. JEE Main: JEE/Main/<year>/...
        m_jee_main = re.match(r"JEE/Main/(\d{4})/(.+)", path, re.I)
        if m_jee_main:
            exam_id = 3
            cat_id = 8
            year = int(m_jee_main.group(1))
            subject_name = "Mathematics"
            title = f"JEE Main {year} Question Paper & Solutions"
            session = "General Session"

        # 6. JEE Advanced: JEE/Advanced/<year>/...
        m_jee_adv = re.match(r"JEE/Advanced/(\d{4})/(?:Paper (\d)|General)/(.+)\.pdf", path, re.I)
        if m_jee_adv:
            exam_id = 3
            cat_id = 9
            year = int(m_jee_adv.group(1))
            paper_no = m_jee_adv.group(2) or "1"
            subject_name = "Physics"
            title = f"JEE Advanced {year} — Paper {paper_no}"
            session = f"Paper {paper_no}"

        # 7. NEET: NEET/<year>/...
        m_neet = re.match(r"NEET/(\d{4})/(.+)/NEET-\d{4}-(.+)-(question|solution)\.pdf", path, re.I)
        if m_neet:
            # Skip standalone solutions as papers; they will be attached to the question paper
            if m_neet.group(4) == "solution":
                continue
            exam_id = 4
            cat_id = 10
            year = int(m_neet.group(1))
            phase_or_set = m_neet.group(3)
            subject_name = "Biology"
            title = f"NEET UG {year} — {phase_or_set} Question Paper"
            session = phase_or_set

        # 8. Tamil Nadu: Boards/Tamil_Nadu/<year>/Tamil_Nadu-<year>-(.+)\.pdf
        m_tn = re.match(r"Boards/Tamil_Nadu/(\d{4})/Tamil_Nadu-\d{4}-(.+)\.pdf", path, re.I)
        if m_tn:
            exam_id = 26
            cat_id = 71
            year = int(m_tn.group(1))
            raw_sub = m_tn.group(2)
            subject_name = clean_subject_name(raw_sub)
            title = f"TN HSC 12th Board {year} — {subject_name} Question Paper"

        if not (exam_id and cat_id and year and title):
            continue

        # Check for matching answer key
        q_base = path.lower().replace("-question.pdf", "")
        ak_url = solution_map.get(q_base)
        has_ak = 1 if ak_url else 0

        # Check if paper with this title or similar exists
        cur.execute("SELECT id, pdf_url FROM papers WHERE exam_category_id = %s AND title = %s", (cat_id, title))
        existing = cur.fetchone()

        if existing:
            # Update to real GitHub raw URL if it had local /uploads/ dummy path
            cur.execute("""
                UPDATE papers SET
                    pdf_url = %s,
                    file_size = %s,
                    source_name = 'GitHub: Shabber10/ALL-PYQ-Papers',
                    source_url = %s,
                    has_answer_key = CASE WHEN %s = 1 THEN 1 ELSE has_answer_key END,
                    answer_key_pdf_url = CASE WHEN %s IS NOT NULL THEN %s ELSE answer_key_pdf_url END,
                    verification_status = 'verified'
                WHERE id = %s
            """, (raw_url, file_size, gh_blob_url, has_ak, ak_url, ak_url, existing["id"]))
            paper_id = existing["id"]
            updated_count += 1
        else:
            # Insert new paper
            cur.execute("""
                INSERT INTO papers (
                    exam_category_id, year, session, title, language, pdf_url,
                    file_size, has_answer_key, answer_key_pdf_url,
                    source_url, source_name, paper_type, verification_status,
                    download_count
                ) VALUES (
                    %s, %s, %s, %s, 'English', %s,
                    %s, %s, %s,
                    %s, 'GitHub: Shabber10/ALL-PYQ-Papers', %s, 'verified',
                    0
                )
            """, (
                cat_id, year, session, title, raw_url,
                file_size, has_ak, ak_url,
                gh_blob_url, paper_type
            ))
            paper_id = cur.lastrowid
            ingested_count += 1

        # Link subject
        subj_id = get_or_create_subject(cur, subject_name)
        cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (paper_id, subj_id))

    conn.commit()
    print(f"✓ Shabber10/ALL-PYQ-Papers: Ingested {ingested_count} new papers, Updated {updated_count} existing papers.")

def sync_avallark_textbooks(conn):
    print("=" * 60)
    print("Fetching GitHub tree for avallark/NCERT-TextBooks...")
    url = "https://api.github.com/repos/avallark/NCERT-TextBooks/git/trees/master?recursive=1"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        tree = data.get("tree", [])

    pdf_items = [x for x in tree if x["path"].lower().endswith(".pdf")]
    print(f"Total textbook PDF documents: {len(pdf_items)}")

    cur = conn.cursor(pymysql.cursors.DictCursor)
    ingested_tb = 0
    updated_tb = 0

    for item in pdf_items:
        path = item["path"]
        raw_url = f"https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/{urllib.parse.quote(path)}"
        gh_blob_url = f"https://github.com/avallark/NCERT-TextBooks/blob/master/{urllib.parse.quote(path)}"
        parts = path.split("/")

        # Standard Level
        standard = "Class 10"
        if path.startswith("10/") or "/10/" in path:
            standard = "Class 10"
        elif path.startswith("11/") or "/11/" in path:
            standard = "Class 11"
        elif path.startswith("12/") or "/12/" in path:
            standard = "Class 12"
        elif path.startswith("9/") or "/9/" in path:
            standard = "Class 9"
        elif path.startswith("8/") or "/8/" in path:
            standard = "Class 8"

        # Determine subject and title
        filename = parts[-1].replace(".pdf", "")
        clean_name = filename.replace("-", " ").replace("_", " ").strip()
        
        subj_name = "Science"
        if "math" in clean_name.lower():
            subj_name = "Mathematics"
        elif "sci" in clean_name.lower() or "physic" in clean_name.lower() or "chem" in clean_name.lower() or "bio" in clean_name.lower():
            subj_name = "Science"
        elif "politi" in clean_name.lower() or "civic" in clean_name.lower() or "democratic" in clean_name.lower():
            subj_name = "Civics"
        elif "geograph" in clean_name.lower() or "contemporary india" in clean_name.lower():
            subj_name = "Geography"
        elif "histor" in clean_name.lower() or "past" in clean_name.lower() or "contemporary world" in clean_name.lower():
            subj_name = "History"
        elif "econom" in clean_name.lower() or "development" in clean_name.lower():
            subj_name = "Economics"
        elif "eng" in clean_name.lower() or "flight" in clean_name.lower():
            subj_name = "English"

        subj_id = get_or_create_subject(cur, subj_name)
        title = f"NCERT {standard} — {clean_name}"

        # Check existing
        cur.execute("SELECT id FROM textbooks WHERE title = %s", (title,))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE textbooks SET
                    pdf_url = %s,
                    source_url = %s,
                    source_name = 'GitHub: avallark/NCERT-TextBooks'
                WHERE id = %s
            """, (raw_url, gh_blob_url, existing["id"]))
            updated_tb += 1
        else:
            cur.execute("""
                INSERT INTO textbooks (
                    standard_level, board, subject_id, title, edition_year,
                    language, pdf_url, source_url, source_name, download_count
                ) VALUES (
                    %s, 'CBSE / NCERT', %s, %s, 2024,
                    'English', %s, %s, 'GitHub: avallark/NCERT-TextBooks', 0
                )
            """, (standard, subj_id, title, raw_url, gh_blob_url))
            ingested_tb += 1

    conn.commit()
    print(f"✓ avallark/NCERT-TextBooks: Ingested {ingested_tb} new textbooks, Updated {updated_tb} existing textbooks.")

def main():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        sync_shabber_pyqs(conn)
        sync_avallark_textbooks(conn)
        print("=" * 60)
        print("ALL GITHUB REPOSITORIES SYNCHRONIZED SUCCESSFULLY!")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
