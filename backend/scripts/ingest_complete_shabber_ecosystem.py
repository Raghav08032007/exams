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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
}

def clean_subject_name(raw: str) -> str:
    s = raw.replace(".pdf", "").replace("-", " ").replace("_", " ").strip().title()
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
        "Gat": "General Ability Test",
        "General Ability And Intelligence": "General Ability & Intelligence",
        "General Knowledge": "General Knowledge",
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
        return row["id"]
    cur.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
    return cur.lastrowid

def get_or_create_exam(cur, name: str, slug: str, desc: str, color: str, official_url: str) -> int:
    cur.execute("SELECT id FROM exams WHERE slug = %s", (slug,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute("""
        INSERT INTO exams (name, slug, description, accent_color_hex, official_site_url)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, slug, desc, color, official_url))
    return cur.lastrowid

def get_or_create_category(cur, exam_id: int, name: str, slug: str, desc: str = "") -> int:
    cur.execute("SELECT id FROM exam_categories WHERE exam_id = %s AND slug = %s", (exam_id, slug))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute("""
        INSERT INTO exam_categories (exam_id, name, slug)
        VALUES (%s, %s, %s)
    """, (exam_id, name, slug))
    return cur.lastrowid

def setup_all_exams_and_categories(cur):
    print("Setting up exam categories...")
    # 1. UPSC (id: 2)
    upsc_id = 2
    cur.execute("SELECT id FROM exams WHERE slug = 'upsc'")
    r = cur.fetchone()
    if r:
        upsc_id = r["id"]

    upsc_categories = [
        ("Civil Services Prelims", "prelims", "Civil Services Preliminary Examination (GS & CSAT)"),
        ("Civil Services Mains", "mains", "Civil Services Main Examination (GS 1-4, Essay, Optionals)"),
        ("National Defence Academy (NDA)", "nda", "NDA & NA Examination (Mathematics & General Ability Test)"),
        ("Combined Defence Services (CDS)", "cds", "CDS Examination (English, General Knowledge, Elementary Mathematics)"),
        ("Central Armed Police Forces (CAPF)", "capf", "CAPF Assistant Commandants Examination"),
        ("Indian Forest Service (IFS)", "ifs", "IFS Main Examination"),
        ("Engineering Services Examination (ESE/IES)", "engineering-services", "UPSC Engineering Services Preliminary & Main"),
        ("Combined Medical Services (CMS)", "cms", "Combined Medical Services Examination"),
    ]
    upsc_cat_map = {}
    for name, slug, desc in upsc_categories:
        cat_id = get_or_create_category(cur, upsc_id, name, slug, desc)
        upsc_cat_map[slug] = cat_id

    # 2. State Boards Exam
    state_exam_id = get_or_create_exam(
        cur,
        "State Boards",
        "state-boards",
        "Official previous year question papers across Indian State Secondary and Higher Secondary Boards.",
        "#0EA5E9",
        "https://www.education.gov.in"
    )

    state_categories = [
        ("Andhra Pradesh Board (BIEAP / BSEAP)", "ap-board", "Andhra Pradesh SSC and Intermediate Papers"),
        ("Bihar Board (BSEB)", "bihar-board", "Bihar School Examination Board Matric & Inter"),
        ("Kerala Board (KBPE / DHSE)", "kerala-board", "Kerala SSLC and Higher Secondary Plus Two"),
        ("Madhya Pradesh Board (MPBSE)", "mp-board", "MP Board High School & Higher Secondary"),
        ("Maharashtra Board (MSBSHSE)", "maharashtra-board", "Maharashtra State Board SSC & HSC"),
        ("Rajasthan Board (RBSE)", "rajasthan-board", "Rajasthan Board Secondary and Senior Secondary"),
        ("Tamil Nadu State Board (DGE)", "tn-board", "Tamil Nadu SSLC 10th and HSC 12th Papers"),
        ("Telangana Board (TSBIE / BSE)", "telangana-board", "Telangana SSC and Intermediate Papers"),
        ("Uttar Pradesh Board (UPMSP)", "up-board", "UP Board High School & Intermediate"),
        ("West Bengal Board (WBBSE / WBCHSE)", "wb-board", "West Bengal Madhyamik & Uchha Madhyamik"),
        ("ICSE / ISC Board (CISCE)", "icse-board", "Council for the Indian School Certificate Examinations"),
    ]
    state_cat_map = {}
    for name, slug, desc in state_categories:
        cat_id = get_or_create_category(cur, state_exam_id, name, slug, desc)
        state_cat_map[slug] = cat_id

    # 3. CBSE Class 10 & 12
    cur.execute("SELECT id FROM exams WHERE slug = 'class-10'")
    c10_id = cur.fetchone()["id"]
    cur.execute("SELECT id FROM exams WHERE slug = 'class-12'")
    c12_id = cur.fetchone()["id"]

    cbse10_cat_id = get_or_create_category(cur, c10_id, "CBSE Class 10", "cbse-10")
    cbse12_cat_id = get_or_create_category(cur, c12_id, "CBSE Class 12", "cbse-12")

    # 4. JEE & NEET
    cur.execute("SELECT id FROM exams WHERE slug = 'jee'")
    jee_id = cur.fetchone()["id"]
    cur.execute("SELECT id FROM exams WHERE slug = 'neet'")
    neet_id = cur.fetchone()["id"]

    jee_main_cat_id = get_or_create_category(cur, jee_id, "JEE Main", "jee-main")
    jee_adv_cat_id = get_or_create_category(cur, jee_id, "JEE Advanced", "jee-advanced")
    neet_cat_id = get_or_create_category(cur, neet_id, "NEET UG", "neet-ug")

    return {
        "upsc_exam_id": upsc_id,
        "upsc_cats": upsc_cat_map,
        "state_exam_id": state_exam_id,
        "state_cats": state_cat_map,
        "c10_id": c10_id,
        "cbse10_cat_id": cbse10_cat_id,
        "c12_id": c12_id,
        "cbse12_cat_id": cbse12_cat_id,
        "jee_id": jee_id,
        "jee_main_cat_id": jee_main_cat_id,
        "jee_adv_cat_id": jee_adv_cat_id,
        "neet_id": neet_id,
        "neet_cat_id": neet_cat_id,
    }

def main():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = conn.cursor()

    config = setup_all_exams_and_categories(cur)
    conn.commit()

    print("Fetching complete GitHub tree from Shabber10/ALL-PYQ-Papers...")
    url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=35) as resp:
        data = json.loads(resp.read().decode())
        tree = data.get("tree", [])

    all_pdfs = [x for x in tree if x["path"].lower().endswith(".pdf")]
    print(f"Total PDFs found in Git Tree: {len(all_pdfs)}")

    # Pre-map all solutions/keys
    solution_map = {}
    for item in all_pdfs:
        p = item["path"]
        low = p.lower()
        if "solution" in low or "answer" in low or "key" in low:
            base_key = low.replace("-solution.pdf", "").replace("-answer.pdf", "").replace("-key.pdf", "")
            solution_map[base_key] = f"https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/{urllib.parse.quote(p)}"

    inserted = 0
    updated = 0
    skipped = 0

    for item in all_pdfs:
        path = item["path"]
        raw_url = f"https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/{urllib.parse.quote(path)}"
        gh_blob_url = f"https://github.com/Shabber10/ALL-PYQ-Papers/blob/main/{urllib.parse.quote(path)}"
        file_size = item.get("size", 2500000)

        exam_cat_id = None
        year = None
        session = None
        subject_name = "General"
        title = ""
        paper_type = "original"
        language = "English"

        parts = path.split("/")

        # Skip standalone solution PDFs from being registered as question papers (they attach as answer keys)
        if "-solution.pdf" in path.lower() or "-answer.pdf" in path.lower():
            continue

        # ── 1. BOARDS / CBSE / 10 ──
        if path.startswith("Boards/CBSE/10/"):
            m = re.match(r"Boards/CBSE/10/(\d{4})/CBSE-Class-10-\d{4}-(.+)\.pdf", path, re.I)
            if m:
                exam_cat_id = config["cbse10_cat_id"]
                year = int(m.group(1))
                subject_name = clean_subject_name(m.group(2))
                title = f"CBSE Class 10 {year} — {subject_name} Question Paper"

        # ── 2. BOARDS / CBSE / 12 ──
        elif path.startswith("Boards/CBSE/12/"):
            m = re.match(r"Boards/CBSE/12/(\d{4})/CBSE-Class-12-\d{4}-(.+)\.pdf", path, re.I)
            if m:
                exam_cat_id = config["cbse12_cat_id"]
                year = int(m.group(1))
                subject_name = clean_subject_name(m.group(2))
                title = f"CBSE Class 12 {year} — {subject_name} Question Paper"

        # ── 3. STATE BOARDS (Bihar, Rajasthan, Maharashtra, AP, Telangana, UP, Kerala, WB, MP, ICSE, TN) ──
        elif path.startswith("Boards/"):
            state_name = parts[1]
            state_key = None
            if state_name == "Bihar": state_key = "bihar-board"
            elif state_name == "Rajasthan": state_key = "rajasthan-board"
            elif state_name == "Maharashtra": state_key = "maharashtra-board"
            elif state_name == "Andhra_Pradesh": state_key = "ap-board"
            elif state_name == "Telangana": state_key = "telangana-board"
            elif state_name == "Uttar_Pradesh": state_key = "up-board"
            elif state_name == "Kerala": state_key = "kerala-board"
            elif state_name == "West_Bengal": state_key = "wb-board"
            elif state_name == "Madhya_Pradesh": state_key = "mp-board"
            elif state_name == "ICSE": state_key = "icse-board"
            elif state_name == "Tamil_Nadu": state_key = "tn-board"

            if state_key and state_key in config["state_cats"]:
                exam_cat_id = config["state_cats"][state_key]
                # Extract year
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                filename = parts[-1].replace(".pdf", "")
                sub_clean = re.sub(r"^[A-Za-z_]+-\d{4}-", "", filename).replace("-", " ").strip().title()
                subject_name = clean_subject_name(sub_clean) or "General"
                disp_state = state_name.replace("_", " ")
                title = f"{disp_state} Board {year} — {subject_name} Question Paper"

        # ── 4. UPSC SUB-EXAMS (Civil Services, NDA, CDS, CAPF, IFS, ESE, CMS) ──
        elif path.startswith("UPSC/"):
            sub_exam = parts[1]

            if sub_exam == "Civil_Services":
                # Prelims or Mains
                stage = parts[2] if len(parts) > 2 else "Mains"
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                if stage.lower() == "prelims":
                    exam_cat_id = config["upsc_cats"]["prelims"]
                    if "paper-ii" in path.lower() or "csat" in path.lower():
                        subject_name = "CSAT"
                        title = f"UPSC Civil Services Prelims {year} — CSAT (Paper II)"
                    else:
                        subject_name = "General Studies"
                        title = f"UPSC Civil Services Prelims {year} — General Studies (Paper I)"
                else:
                    exam_cat_id = config["upsc_cats"]["mains"]
                    filename = parts[-1].replace(".pdf", "")
                    sub_raw = re.sub(r"^UPSC-CSE-Mains-\d{4}-", "", filename).replace("-", " ").strip().title()
                    subject_name = clean_subject_name(sub_raw)
                    title = f"UPSC Civil Services Mains {year} — {subject_name}"

            elif sub_exam == "NDA":
                exam_cat_id = config["upsc_cats"]["nda"]
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                filename = parts[-1].replace(".pdf", "")
                sess = "NDA 1" if "nda-1" in filename.lower() or "nda 1" in filename.lower() else "NDA 2"
                sub_raw = "Mathematics" if "math" in filename.lower() else "General Ability Test (GAT)"
                subject_name = clean_subject_name(sub_raw)
                session = sess
                title = f"UPSC NDA {year} ({sess}) — {subject_name} Question Paper"

            elif sub_exam == "CDS":
                exam_cat_id = config["upsc_cats"]["cds"]
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                filename = parts[-1].replace(".pdf", "")
                sess = "CDS 1" if "cds-1" in filename.lower() or "cds 1" in filename.lower() else "CDS 2"
                sub_raw = "English" if "english" in filename.lower() else ("Mathematics" if "math" in filename.lower() else "General Knowledge")
                subject_name = clean_subject_name(sub_raw)
                session = sess
                title = f"UPSC CDS {year} ({sess}) — {subject_name} Question Paper"

            elif sub_exam == "CAPF":
                exam_cat_id = config["upsc_cats"]["capf"]
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                filename = parts[-1].replace(".pdf", "")
                sub_raw = "Essay, Précis & Comprehension" if "essay" in filename.lower() else "General Ability and Intelligence"
                subject_name = clean_subject_name(sub_raw)
                title = f"UPSC CAPF {year} — {subject_name} Question Paper"

            elif sub_exam == "Indian_Forest_Service":
                exam_cat_id = config["upsc_cats"]["ifs"]
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                filename = parts[-1].replace(".pdf", "")
                sub_raw = re.sub(r"^UPSC-Indian_Forest_Service-\d{4}-", "", filename).replace("-", " ").strip().title()
                subject_name = clean_subject_name(sub_raw)
                title = f"UPSC IFS {year} — {subject_name}"

            elif sub_exam == "Engineering_Services":
                exam_cat_id = config["upsc_cats"]["engineering-services"]
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                filename = parts[-1].replace(".pdf", "")
                sub_raw = re.sub(r"^UPSC-Engineering_Services-\d{4}-", "", filename).replace("-", " ").strip().title()
                subject_name = clean_subject_name(sub_raw)
                title = f"UPSC ESE/IES {year} — {subject_name}"

            elif sub_exam == "Combined_Medical_Services":
                exam_cat_id = config["upsc_cats"]["cms"]
                y_m = re.search(r"(\d{4})", path)
                year = int(y_m.group(1)) if y_m else 2020
                filename = parts[-1].replace(".pdf", "")
                sub_raw = "Paper I" if "paper-i" in filename.lower() else "Paper II"
                subject_name = "Medical Science"
                title = f"UPSC CMS {year} — {sub_raw}"

        # ── 5. JEE (Main & Advanced) ──
        elif path.startswith("JEE/"):
            jee_type = parts[1]
            y_m = re.search(r"(\d{4})", path)
            year = int(y_m.group(1)) if y_m else 2022

            if jee_type.lower() == "main":
                exam_cat_id = config["jee_main_cat_id"]
                subject_name = "Mathematics"
                title = f"JEE Main {year} Question Paper & Solutions"
                session = "Shift 1 / General"
            else:
                exam_cat_id = config["jee_adv_cat_id"]
                paper_no = "2" if "paper 2" in path.lower() or "paper-2" in path.lower() else "1"
                subject_name = "Physics"
                session = f"Paper {paper_no}"
                title = f"JEE Advanced {year} — Paper {paper_no}"

        # ── 6. NEET ──
        elif path.startswith("NEET/"):
            exam_cat_id = config["neet_cat_id"]
            y_m = re.search(r"(\d{4})", path)
            year = int(y_m.group(1)) if y_m else 2023
            filename = parts[-1].replace(".pdf", "")
            set_match = re.search(r"-([A-Za-z0-9_]+)-(question|solution)", filename, re.I)
            set_name = set_match.group(1) if set_match else "Main"
            subject_name = "Biology"
            session = f"Set {set_name}"
            title = f"NEET UG {year} — {set_name} Question Paper"

        if not (exam_cat_id and year and title):
            skipped += 1
            continue

        # Look up co-located solution key
        q_base = path.lower().replace("-question.pdf", "")
        ak_url = solution_map.get(q_base)
        has_ak = 1 if ak_url else 0

        # Upsert into papers
        cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND title = %s", (exam_cat_id, title))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE papers SET
                    year = %s,
                    session = %s,
                    pdf_url = %s,
                    file_size = %s,
                    source_name = 'GitHub: Shabber10/ALL-PYQ-Papers',
                    source_url = %s,
                    has_answer_key = CASE WHEN %s = 1 THEN 1 ELSE has_answer_key END,
                    answer_key_pdf_url = CASE WHEN %s IS NOT NULL THEN %s ELSE answer_key_pdf_url END,
                    verification_status = 'verified'
                WHERE id = %s
            """, (year, session, raw_url, file_size, gh_blob_url, has_ak, ak_url, ak_url, existing["id"]))
            paper_id = existing["id"]
            updated += 1
        else:
            cur.execute("""
                INSERT INTO papers (
                    exam_category_id, year, session, title, language, pdf_url,
                    file_size, has_answer_key, answer_key_pdf_url,
                    source_url, source_name, paper_type, verification_status,
                    download_count
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, 'GitHub: Shabber10/ALL-PYQ-Papers', %s, 'verified',
                    0
                )
            """, (
                exam_cat_id, year, session, title, language, raw_url,
                file_size, has_ak, ak_url,
                gh_blob_url, paper_type
            ))
            paper_id = cur.lastrowid
            inserted += 1

        # Link subject
        subj_id = get_or_create_subject(cur, subject_name)
        cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (paper_id, subj_id))

    conn.commit()

    print("=" * 60)
    print(f"COMPLETE SHABBER INGESTION RESULT:")
    print(f"  Inserted: {inserted} new papers")
    print(f"  Updated:  {updated} papers")
    print(f"  Skipped:  {skipped} non-paper files")
    
    cur.execute("SELECT COUNT(*) as total FROM papers")
    total_in_db = cur.fetchone()["total"]
    print(f"  Total verified papers in database now: {total_in_db}")
    print("=" * 60)

    conn.close()

if __name__ == "__main__":
    main()
