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

papers_2020 = [
    {
        'sub_id': 147,
        'title': 'Tamil Nadu SSLC Class 10 Tamil Question Paper 2020 (Revision Public Exam)',
        'pdf_url': 'https://www.educationobserver.com/forum/attachment.php?aid=38433',
        'key_url': 'https://www.educationobserver.com/forum/attachment.php?aid=38434',
        'lang': 'Tamil'
    },
    {
        'sub_id': 815,
        'title': 'Tamil Nadu SSLC Class 10 English Question Paper 2020 (Revision Public Exam)',
        'pdf_url': 'https://www.educationobserver.com/forum/attachment.php?aid=38731',
        'key_url': None,
        'lang': 'English'
    },
    {
        'sub_id': 28,
        'title': 'Tamil Nadu SSLC Class 10 Science Question Paper 2020 (Revision Public Exam - EM)',
        'pdf_url': 'https://www.educationobserver.com/forum/attachment.php?aid=38784',
        'key_url': None,
        'lang': 'English'
    },
    {
        'sub_id': 28,
        'title': 'Tamil Nadu SSLC Class 10 Science Question Paper 2020 (Revision Public Exam - TM)',
        'pdf_url': 'https://www.educationobserver.com/forum/attachment.php?aid=38783',
        'key_url': None,
        'lang': 'Tamil'
    },
    {
        'sub_id': 90,
        'title': 'Tamil Nadu SSLC Class 10 Social Science Question Paper 2020 (Revision Public Exam)',
        'pdf_url': 'https://www.educationobserver.com/forum/attachment.php?aid=38734',
        'key_url': None,
        'lang': 'Tamil & English'
    }
]

cur = conn.cursor()
for p in papers_2020:
    for cat_id in [67, 2626]:
        cur.execute(
            "SELECT id FROM papers WHERE exam_category_id = %s AND pdf_url = %s",
            (cat_id, p['pdf_url'])
        )
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO papers (
                    exam_category_id, year, session, title, language, pdf_url, 
                    has_answer_key, answer_key_pdf_url, verification_status,
                    source_url, source_name, paper_type
                ) VALUES (
                    %s, 2020, 'Revision Public Exam', %s, %s, %s,
                    %s, %s, 'verified',
                    'https://www.educationobserver.com/tamilnadu-sslc-exam-2020-revision-question-papers/',
                    'Tamil Nadu Directorate of Government Examinations (DGE)', 'Official Public Exam'
                )
            """, (
                cat_id, p['title'], p['lang'], p['pdf_url'],
                1 if p['key_url'] else 0, p['key_url']
            ))
            pid = cur.lastrowid
            cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (pid, p['sub_id']))

print("Added 2020 missing papers!")
conn.close()
