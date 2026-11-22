import os
import sys
import ssl
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import pymysql.cursors

sys.path.insert(0, os.path.abspath('backend'))

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HEADERS = {'User-Agent': 'Mozilla/5.0'}

RAW_BASE = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/"

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL", "mysql+pymysql://root:261008@localhost:3306/examvault")
    for prefix in ("mysql+pymysql://", "mysql://", "pymysql://"):
        if db_url.startswith(prefix):
            db_url = "mysql://" + db_url[len(prefix):]
            break
    parsed = urlparse(db_url)
    return pymysql.connect(
        host=parsed.hostname or "localhost",
        port=parsed.port or 3306,
        user=parsed.username or "root",
        password=parsed.password or "",
        database=parsed.path.lstrip("/") or "examvault",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def download_and_validate(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        with open(dest_path, 'rb') as f:
            if f.read(5) == b'%PDF-':
                return True, os.path.getsize(dest_path)
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
            data = resp.read()
            if not data.startswith(b'%PDF-'):
                return False, 0
            with open(dest_path, 'wb') as f:
                f.write(data)
            return True, len(data)
    except Exception as e:
        print(f"Error {url}: {e}")
        return False, 0

def tag_subjects(cursor, paper_id, subject_names):
    for subj_name in subject_names:
        cursor.execute("INSERT INTO subjects (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (subj_name,))
        cursor.execute("SELECT id FROM subjects WHERE name = %s", (subj_name,))
        row = cursor.fetchone()
        if row:
            s_id = row['id']
            cursor.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (paper_id, s_id))

def get_cat_id(cursor, exam_slug, cat_slug):
    cursor.execute("""
        SELECT ec.id FROM exam_categories ec 
        JOIN exams e ON ec.exam_id = e.id 
        WHERE e.slug = %s AND ec.slug = %s
    """, (exam_slug, cat_slug))
    row = cursor.fetchone()
    return row['id'] if row else None

TARGET_PAPERS = [
    # Tamil Nadu SSLC (Class 10) with distinct titles
    {"exam": "class-10", "cat": "tn-sslc", "year": 2020, "session": "Public Exam", "title": "Tamil Nadu SSLC 2020 - Mathematics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2020/Tamil_Nadu-2020-mathematics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Mathematics"]},
    {"exam": "class-10", "cat": "tn-sslc", "year": 2018, "session": "Public Exam", "title": "Tamil Nadu SSLC 2018 - Mathematics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2018/Tamil_Nadu-2018-mathematics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Mathematics"]},
    {"exam": "class-10", "cat": "tn-sslc", "year": 2017, "session": "Public Exam", "title": "Tamil Nadu SSLC 2017 - Mathematics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2017/Tamil_Nadu-2017-mathematics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Mathematics"]},
    {"exam": "class-10", "cat": "tn-sslc", "year": 2016, "session": "Public Exam", "title": "Tamil Nadu SSLC 2016 - Mathematics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2016/Tamil_Nadu-2016-mathematics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Mathematics"]},
    {"exam": "class-10", "cat": "tn-sslc", "year": 2015, "session": "Public Exam", "title": "Tamil Nadu SSLC 2015 - Mathematics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2015/Tamil_Nadu-2015-mathematics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Mathematics"]},

    # Tamil Nadu HSC (Class 12) with distinct titles
    {"exam": "class-12", "cat": "tn-hsc", "year": 2020, "session": "Public Exam", "title": "Tamil Nadu HSC 2020 - Physics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2020/Tamil_Nadu-2020-physics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Physics"]},
    {"exam": "class-12", "cat": "tn-hsc", "year": 2018, "session": "Public Exam", "title": "Tamil Nadu HSC 2018 - Economics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2018/Tamil_Nadu-2018-economics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Economics"]},
    {"exam": "class-12", "cat": "tn-hsc", "year": 2017, "session": "Public Exam", "title": "Tamil Nadu HSC 2017 - Accountancy Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2017/Tamil_Nadu-2017-accountancy.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Accountancy"]},
    {"exam": "class-12", "cat": "tn-hsc", "year": 2016, "session": "Public Exam", "title": "Tamil Nadu HSC 2016 - Accountancy Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2016/Tamil_Nadu-2016-accountancy.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Accountancy"]},
    {"exam": "class-12", "cat": "tn-hsc", "year": 2015, "session": "Public Exam", "title": "Tamil Nadu HSC 2015 - Physics Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2015/Tamil_Nadu-2015-physics.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Physics"]},
    {"exam": "class-12", "cat": "tn-hsc", "year": 2015, "session": "Public Exam", "title": "Tamil Nadu HSC 2015 - Chemistry Public Examination Question Paper", "lang": "English / Tamil", "url": RAW_BASE + urllib.parse.quote("Boards/Tamil_Nadu/2015/Tamil_Nadu-2015-chemistry.pdf"), "source_name": "Tamil Nadu Directorate of Government Examinations (dge.tn.gov.in / State Archive)", "subjs": ["Chemistry"]},

    # Additional JEE Main
    {"exam": "jee", "cat": "jee-main", "year": 2016, "session": "Main", "title": "JEE Main 2016 - Official Question Paper & Complete Solutions", "lang": "English", "url": RAW_BASE + urllib.parse.quote("JEE/Main/2016/General/JEE-Main-2016-General-5aa8df16e4b05c43726dc8d7.pdf"), "source_name": "National Testing Agency (NTA Verified Archive)", "subjs": ["Physics", "Chemistry", "Mathematics"], "has_ans": 1},
    {"exam": "jee", "cat": "jee-main", "year": 2015, "session": "Main", "title": "JEE Main 2015 - Official Question Paper & Solutions (General)", "lang": "English", "url": RAW_BASE + urllib.parse.quote("JEE/Main/2015/General/JEE-Main-2015-General-5aa8ee6ee4b05c43726dc97a.pdf"), "source_name": "National Testing Agency (NTA Verified Archive)", "subjs": ["Physics", "Chemistry", "Mathematics"], "has_ans": 1},
]

def main():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        for item in TARGET_PAPERS:
            cat_id = get_cat_id(cursor, item['exam'], item['cat'])
            if not cat_id:
                print(f"Skipping {item['title']}: cat not found")
                continue

            clean_title = "".join(c if c.isalnum() or c in "._-" else "_" for c in item['title'].replace(" ", "_"))
            dest_dir = os.path.join("backend", "uploads", "papers", item['exam'])
            os.makedirs(dest_dir, exist_ok=True)
            dest_pdf = os.path.join(dest_dir, f"{clean_title}.pdf")

            ok, size = download_and_validate(item['url'], dest_pdf)
            if not ok:
                print(f"Failed download: {item['title']}")
                continue

            pdf_web_url = f"/uploads/papers/{item['exam']}/{os.path.basename(dest_pdf)}"
            cursor.execute("SELECT id FROM papers WHERE title = %s OR pdf_url = %s", (item['title'], pdf_web_url))
            existing = cursor.fetchone()

            has_ans = item.get('has_ans', 0)

            if existing:
                paper_id = existing['id']
                cursor.execute("""
                    UPDATE papers SET
                        exam_category_id = %s, year = %s, session = %s, language = %s,
                        pdf_url = %s, file_size = %s, has_answer_key = %s,
                        verification_status = 'verified', source_url = %s, source_name = %s
                    WHERE id = %s
                """, (cat_id, item['year'], item['session'], item['lang'], pdf_web_url, size, has_ans, item['url'], item['source_name'], paper_id))
            else:
                cursor.execute("""
                    INSERT INTO papers (
                        exam_category_id, year, session, title, language,
                        pdf_url, file_size, has_answer_key, download_count,
                        verification_status, upload_date, source_url, source_name
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, 'verified', NOW(), %s, %s)
                """, (cat_id, item['year'], item['session'], item['title'], item['lang'], pdf_web_url, size, has_ans, item['url'], item['source_name']))
                paper_id = cursor.lastrowid

            tag_subjects(cursor, paper_id, item['subjs'])
            status = "UPDATED" if existing else "INGESTED"
            print(f"{status}: {item['title']} ({size / (1024*1024):.2f} MB)")

    conn.close()

if __name__ == '__main__':
    main()
