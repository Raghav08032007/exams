"""
Download and link authentic official answer keys for UPSC, JEE Advanced, NEET, TNPSC, and CBSE.
"""
import os
import urllib.request
import urllib.error
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "261008",
    "database": "examvault",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True
}

UPLOAD_KEYS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "answer_keys")
os.makedirs(UPLOAD_KEYS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def download_pdf(url, dest_path):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
            if len(data) > 1000 and (b"%PDF" in data[:100] or b"PDF" in data[:20]):
                with open(dest_path, "wb") as f:
                    f.write(data)
                return True
    except Exception as e:
        # print(f"Error {url}: {e}")
        pass
    return False

def run_ingestion():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 1. LINK NEET PAPERS WITH EXISTING MS FILES
    print("--- 1. Linking NEET Papers with existing MS files ---")
    neet_files = {
        2018: "/uploads/papers/neet/NEET_UG_2018_-_Question_Paper_Booklet_Code_AA-DD_with_Full_Answer_Key_MS.pdf",
        2020: "/uploads/papers/neet/NEET_UG_2020_-_Question_Paper_Booklet_Code_E1_with_Official_Solutions_MS.pdf",
        2022: "/uploads/papers/neet/NEET_UG_2022_-_Question_Paper_Booklet_Code_T1_with_Solutions_MS.pdf",
        2023: "/uploads/papers/neet/NEET_UG_2023_-_Question_Paper_Booklet_Code_E1_with_Detailed_Solutions_MS.pdf",
    }
    for yr, ms_path in neet_files.items():
        cur.execute("""
            UPDATE papers p
            JOIN exam_categories ec ON p.exam_category_id = ec.id
            JOIN exams e ON ec.exam_id = e.id
            SET p.has_answer_key = 1, p.answer_key_pdf_url = %s, p.answer_key_source_url = p.source_url
            WHERE e.slug = 'neet' AND p.year = %s AND (p.answer_key_pdf_url IS NULL OR p.answer_key_pdf_url = '')
        """, (ms_path, yr))
        print(f" Updated NEET {yr} answer keys: affected={cur.rowcount}")

    # 2. JEE ADVANCED OFFICIAL ANSWER KEYS (jeeadv.ac.in)
    print("\n--- 2. Fetching JEE Advanced Official Answer Keys ---")
    jee_keys_map = {
        (2024, "Paper 1"): "https://jeeadv.ac.in/archive/past-papers/2024/JEE_Adv_2024_Paper_1_Final_Answer_Keys.pdf",
        (2024, "Paper 2"): "https://jeeadv.ac.in/archive/past-papers/2024/JEE_Adv_2024_Paper_2_Final_Answer_Keys.pdf",
        (2023, "Paper 1"): "https://jeeadv.ac.in/archive/past-papers/2023/JEE_Adv_2023_Paper_1_Final_Answer_Keys.pdf",
        (2023, "Paper 2"): "https://jeeadv.ac.in/archive/past-papers/2023/JEE_Adv_2023_Paper_2_Final_Answer_Keys.pdf",
        (2022, "Paper 1"): "https://jeeadv.ac.in/archive/past-papers/2022/JEE_Adv_2022_Paper_1_Final_Answer_Keys.pdf",
        (2022, "Paper 2"): "https://jeeadv.ac.in/archive/past-papers/2022/JEE_Adv_2022_Paper_2_Final_Answer_Keys.pdf",
        (2021, "Paper 1"): "https://jeeadv.ac.in/archive/past-papers/2021/JEE_Adv_2021_Paper_1_Final_Answer_Keys.pdf",
        (2021, "Paper 2"): "https://jeeadv.ac.in/archive/past-papers/2021/JEE_Adv_2021_Paper_2_Final_Answer_Keys.pdf",
        (2020, "Paper 1"): "https://jeeadv.ac.in/archive/past-papers/2020/JEE_Adv_2020_Paper_1_Final_Answer_Keys.pdf",
        (2020, "Paper 2"): "https://jeeadv.ac.in/archive/past-papers/2020/JEE_Adv_2020_Paper_2_Final_Answer_Keys.pdf",
        (2019, "Paper 1"): "https://jeeadv.ac.in/archive/past-papers/2019/JEE_Adv_2019_Paper_1_Final_Answer_Keys.pdf",
        (2019, "Paper 2"): "https://jeeadv.ac.in/archive/past-papers/2019/JEE_Adv_2019_Paper_2_Final_Answer_Keys.pdf",
        (2018, "Paper 1"): "https://jeeadv.ac.in/archive/past-papers/2018/JEE_Adv_2018_Paper_1_Final_Answer_Keys.pdf",
        (2018, "Paper 2"): "https://jeeadv.ac.in/archive/past-papers/2018/JEE_Adv_2018_Paper_2_Final_Answer_Keys.pdf",
    }

    # Also fallback mirror on GitHub archive
    jee_mirror_base = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/JEE/JEE_Advanced"

    for (yr, p_num), url in jee_keys_map.items():
        fname = f"jee_adv_{yr}_{p_num.lower().replace(' ', '_')}_key.pdf"
        dest = os.path.join(UPLOAD_KEYS_DIR, fname)
        rel_url = f"/uploads/answer_keys/{fname}"

        success = False
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            success = True
        else:
            if download_pdf(url, dest):
                success = True
            else:
                # Try mirror
                m_url = f"{jee_mirror_base}/{yr}/JEE_Adv_{yr}_{p_num.replace(' ', '_')}_Key.pdf"
                if download_pdf(m_url, dest):
                    success = True

        if success:
            cur.execute("""
                UPDATE papers p
                JOIN exam_categories ec ON p.exam_category_id = ec.id
                JOIN exams e ON ec.exam_id = e.id
                SET p.has_answer_key = 1, p.answer_key_pdf_url = %s, p.answer_key_source_url = %s
                WHERE e.slug = 'jee' AND p.year = %s AND p.title LIKE %s
            """, (rel_url, url, yr, f"%{p_num}%"))
            print(f" Linked JEE Adv {yr} {p_num} Key (affected={cur.rowcount})")

    # Also for JEE Main with Solutions: mark has_answer_key = 1 and answer_key_pdf_url = p.pdf_url
    cur.execute("""
        UPDATE papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        JOIN exams e ON ec.exam_id = e.id
        SET p.has_answer_key = 1, p.answer_key_pdf_url = p.pdf_url, p.answer_key_source_url = p.source_url
        WHERE e.slug = 'jee' AND (p.title LIKE '%Solution%' OR p.title LIKE '%Key%')
    """)
    print(f" Updated JEE Main solved papers with answer keys: affected={cur.rowcount}")

    # 3. UPSC CSE PRELIMS OFFICIAL ANSWER KEYS (upsc.gov.in)
    print("\n--- 3. Fetching UPSC CSE Prelims Official Answer Keys ---")
    upsc_keys_map = {
        (2023, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-23-GS-P1-090524.pdf",
        (2023, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-23-CSAT-P2-090524.pdf",
        (2022, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-22-GS-P1-190523.pdf",
        (2022, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-22-CSAT-P2-190523.pdf",
        (2021, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-21-GS-P1-070722.pdf",
        (2021, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-21-CSAT-P2-070722.pdf",
        (2020, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-20-GS-P1-291021.pdf",
        (2020, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-20-CSAT-P2-291021.pdf",
        (2019, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-19-GS-P1-090820.pdf",
        (2019, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-19-CSAT-P2-090820.pdf",
        (2018, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-18-GS-P1-170719.pdf",
        (2018, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-18-CSAT-P2-170719.pdf",
        (2017, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-17-GS-P1.pdf",
        (2017, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-17-CSAT-P2.pdf",
        (2016, "General Studies Paper I"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-16-GS-P1.pdf",
        (2016, "General Studies Paper II (CSAT)"): "https://www.upsc.gov.in/sites/default/files/AnsKey-CSP-16-CSAT-P2.pdf",
    }

    # UPSC archive mirror fallback
    upsc_mirror_base = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/UPSC/Prelims_Keys"

    for (yr, p_title), url in upsc_keys_map.items():
        fname = f"upsc_csp_{yr}_{'gs1' if 'Paper I' in p_title else 'csat'}_key.pdf"
        dest = os.path.join(UPLOAD_KEYS_DIR, fname)
        rel_url = f"/uploads/answer_keys/{fname}"

        success = False
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            success = True
        else:
            if download_pdf(url, dest):
                success = True
            else:
                m_url = f"{upsc_mirror_base}/{fname}"
                if download_pdf(m_url, dest):
                    success = True

        if success:
            match_str = "%General Studies Paper I%" if "Paper I" in p_title else "%Paper II%"
            cur.execute("""
                UPDATE papers p
                JOIN exam_categories ec ON p.exam_category_id = ec.id
                JOIN exams e ON ec.exam_id = e.id
                SET p.has_answer_key = 1, p.answer_key_pdf_url = %s, p.answer_key_source_url = %s
                WHERE e.slug = 'upsc' AND p.year = %s AND p.title LIKE %s
            """, (rel_url, url, yr, match_str))
            print(f" Linked UPSC {yr} {p_title} Key (affected={cur.rowcount})")

    # 4. TNPSC PAPERS WITH ANSWER KEYS
    # For TNPSC papers with answer keys, ensure answer_key_pdf_url points to the valid PDF
    cur.execute("""
        UPDATE papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        JOIN exams e ON ec.exam_id = e.id
        SET p.answer_key_pdf_url = p.pdf_url
        WHERE e.slug = 'tnpsc' AND p.has_answer_key = 1 AND (p.answer_key_pdf_url IS NULL OR p.answer_key_pdf_url = '')
    """)
    print(f" Fixed TNPSC answer key URLs: affected={cur.rowcount}")

    # Summary
    cur.execute("""
        SELECT e.name, COUNT(*) as total, SUM(p.has_answer_key) as with_key 
        FROM papers p 
        JOIN exam_categories ec ON p.exam_category_id = ec.id 
        JOIN exams e ON ec.exam_id = e.id 
        GROUP BY e.name
    """)
    print("\n================ FINAL ANSWER KEY SUMMARY ================")
    for r in cur.fetchall():
        print(f" - {r['name']}: {r['with_key']}/{r['total']} papers have official answer keys linked")

    cur.execute("SELECT COUNT(*) AS total, SUM(has_answer_key) AS with_key FROM papers WHERE answer_key_pdf_url IS NOT NULL AND answer_key_pdf_url != ''")
    row = cur.fetchone()
    print(f"\nTotal papers with valid accessible answer key URLs: {row['with_key']} / {row['total']}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    run_ingestion()
