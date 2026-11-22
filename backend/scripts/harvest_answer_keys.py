"""
Harvest official answer keys for JEE Advanced, UPSC, NEET, CBSE, and TNPSC.
Downloads PDFs locally and updates papers table:
  - has_answer_key = 1
  - answer_key_pdf_url = '/uploads/answer_keys/...'
"""
import os
import urllib.request
import urllib.parse
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

UPLOAD_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "answer_keys")
os.makedirs(UPLOAD_BASE, exist_ok=True)

# Sources for Official Answer Keys:
# 1. JEE Advanced: Official answer keys hosted on jeeadv.ac.in archives
JEE_ADV_KEYS = {
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

# UPSC Prelims Official Final Answer Keys
UPSC_KEYS = {
    (2023, "General Studies Paper I"): "https://upsc.gov.in/sites/default/files/CSP-2023-GS-P1-AnsKey.pdf",
    (2023, "General Studies Paper II (CSAT)"): "https://upsc.gov.in/sites/default/files/CSP-2023-CSAT-AnsKey.pdf",
    (2022, "General Studies Paper I"): "https://upsc.gov.in/sites/default/files/CSP-2022-GS-P1-AnsKey.pdf",
    (2022, "General Studies Paper II (CSAT)"): "https://upsc.gov.in/sites/default/files/CSP-2022-CSAT-AnsKey.pdf",
    (2021, "General Studies Paper I"): "https://upsc.gov.in/sites/default/files/CSP-2021-GS-P1-AnsKey.pdf",
    (2021, "General Studies Paper II (CSAT)"): "https://upsc.gov.in/sites/default/files/CSP-2021-CSAT-AnsKey.pdf",
    (2020, "General Studies Paper I"): "https://upsc.gov.in/sites/default/files/CSP-2020-GS-P1-AnsKey.pdf",
    (2020, "General Studies Paper II (CSAT)"): "https://upsc.gov.in/sites/default/files/CSP-2020-CSAT-AnsKey.pdf",
    (2019, "General Studies Paper I"): "https://upsc.gov.in/sites/default/files/CSP-2019-GS-P1-AnsKey.pdf",
    (2019, "General Studies Paper II (CSAT)"): "https://upsc.gov.in/sites/default/files/CSP-2019-CSAT-AnsKey.pdf",
}

# GitHub Archive mirror for verified keys:
GITHUB_MIRROR = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main"

def download_file(url, out_path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp, open(out_path, "wb") as f:
            content = resp.read()
            if len(content) > 500 and b"%PDF" in content[:100]:
                f.write(content)
                return True
            else:
                return False
    except Exception as e:
        return False

def sync_existing_keys():
    """Sync all already-downloaded keys on disk with the database."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        # Check files in backend/uploads/papers/class-10
        cur.execute("SELECT id, title, year, pdf_url FROM papers")
        all_papers = cur.fetchall()

        updated_count = 0
        for p in all_papers:
            pdf_url = p.get("pdf_url") or ""
            # If pdf_url is /uploads/papers/class-10/cbse10_2024_maths_std.pdf
            # Check if key cbse10_2024_maths_std_key.pdf exists
            if "_key.pdf" not in pdf_url and pdf_url.endswith(".pdf"):
                key_relative = pdf_url.replace(".pdf", "_key.pdf")
                key_disk = os.path.join(os.path.dirname(UPLOAD_BASE), key_relative.lstrip("/uploads/"))
                if os.path.exists(key_disk) and os.path.getsize(key_disk) > 1000:
                    cur.execute("""
                        UPDATE papers 
                        SET has_answer_key = 1, answer_key_pdf_url = %s, answer_key_source_url = source_url
                        WHERE id = %s
                    """, (key_relative, p["id"]))
                    updated_count += 1
                
                # Check with _MS.pdf as well
                ms_relative = pdf_url.replace(".pdf", "_MS.pdf")
                ms_disk = os.path.join(os.path.dirname(UPLOAD_BASE), ms_relative.lstrip("/uploads/"))
                if os.path.exists(ms_disk) and os.path.getsize(ms_disk) > 1000:
                    cur.execute("""
                        UPDATE papers 
                        SET has_answer_key = 1, answer_key_pdf_url = %s, answer_key_source_url = source_url
                        WHERE id = %s
                    """, (ms_relative, p["id"]))
                    updated_count += 1

        print(f"Synced {updated_count} existing disk answer keys into database.")

        # Next: For CBSE SQP papers that have source_url ending in -SQP.pdf, download -MS.pdf
        cur.execute("SELECT id, title, year, source_url, pdf_url FROM papers WHERE source_url LIKE '%-SQP.pdf%' OR source_url LIKE '%SQP.pdf%'")
        sqp_papers = cur.fetchall()
        print(f"Found {len(sqp_papers)} CBSE SQP papers to verify marking schemes...")
        
        cbse_keys_count = 0
        for p in sqp_papers:
            src = p["source_url"]
            ms_url = src.replace("-SQP.pdf", "-MS.pdf").replace("SQP.pdf", "MS.pdf")
            filename = f"cbse_ms_{p['id']}_{p['year']}.pdf"
            out_file = os.path.join(UPLOAD_BASE, filename)
            rel_url = f"/uploads/answer_keys/{filename}"
            
            if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
                cur.execute("""
                    UPDATE papers SET has_answer_key = 1, answer_key_pdf_url = %s, answer_key_source_url = %s
                    WHERE id = %s
                """, (rel_url, ms_url, p["id"]))
                cbse_keys_count += 1
            else:
                if download_file(ms_url, out_file):
                    cur.execute("""
                        UPDATE papers SET has_answer_key = 1, answer_key_pdf_url = %s, answer_key_source_url = %s
                        WHERE id = %s
                    """, (rel_url, ms_url, p["id"]))
                    cbse_keys_count += 1
                    print(f" Downloaded MS for: {p['title']}")

        print(f"CBSE Marking Schemes active: {cbse_keys_count}")

        # Summary of papers with answer keys
        cur.execute("SELECT COUNT(*) AS total, SUM(has_answer_key) AS with_key FROM papers")
        res = cur.fetchone()
        print(f"\nUpdated DB Summary: Total={res['total']}, With Answer Key={res['with_key']}")

    conn.close()

if __name__ == "__main__":
    sync_existing_keys()
