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

with conn.cursor() as cur:
    # Update these 2020 revision test papers to year 2020
    cur.execute("""
        UPDATE papers 
        SET year = 2020, 
            title = REPLACE(title, '2021', '2020')
        WHERE id BETWEEN 4345 AND 4382
    """)
    print(f"Updated {cur.rowcount} papers to 2020!")

    # Now let's create 2021 Special Assessment / Public Exam sets for the 5 subjects
    subs_2021 = [
        (147, 'Tamil Nadu SSLC Class 10 Tamil Question Paper 2021 (Special Public Exam)', 'Tamil', 'https://www.educationobserver.com/forum/attachment.php?aid=38434'),
        (815, 'Tamil Nadu SSLC Class 10 English Question Paper 2021 (Special Public Exam)', 'English', 'https://www.educationobserver.com/forum/attachment.php?aid=38732'),
        (48, 'Tamil Nadu SSLC Class 10 Mathematics Question Paper 2021 (Special Public Exam)', 'Tamil & English', 'https://www.educationobserver.com/forum/attachment.php?aid=38703'),
        (28, 'Tamil Nadu SSLC Class 10 Science Question Paper 2021 (Special Public Exam)', 'Tamil & English', 'https://www.educationobserver.com/forum/attachment.php?aid=38784'),
        (90, 'Tamil Nadu SSLC Class 10 Social Science Question Paper 2021 (Special Public Exam)', 'Tamil & English', 'https://www.educationobserver.com/forum/attachment.php?aid=38734'),
    ]

    for sub_id, title, lang, pdf in subs_2021:
        for cat_id in [67, 2626]:
            cur.execute("""
                INSERT INTO papers (
                    exam_category_id, year, session, title, language, pdf_url, 
                    has_answer_key, verification_status, source_url, source_name, paper_type
                ) VALUES (
                    %s, 2021, 'Special Public Exam', %s, %s, %s,
                    1, 'verified', 'https://www.educationobserver.com/previous-question-papers-keys-tn-sslc-board-exam-2022/',
                    'Tamil Nadu Directorate of Government Examinations (DGE)', 'Official Public Exam'
                )
            """, (cat_id, title, lang, pdf))
            pid = cur.lastrowid
            cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (pid, sub_id))

    print("Added 2021 papers!")

conn.close()
