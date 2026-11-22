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
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) as cnt FROM chapters")
    ch_cnt = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM chapter_questions")
    q_cnt = cur.fetchone()['cnt']
    print(f"Total Chapters: {ch_cnt}, Total Questions: {q_cnt}")

    cur.execute("""
        SELECT s.name as subject, COUNT(DISTINCT c.id) as ch_cnt, COUNT(cq.id) as q_cnt
        FROM chapters c
        JOIN subjects s ON c.subject_id = s.id
        LEFT JOIN chapter_questions cq ON c.id = cq.chapter_id
        GROUP BY s.name
        ORDER BY ch_cnt DESC
    """)
    rows = cur.fetchall()
    print("\n=== Chapters & Questions per Subject ===")
    for r in rows:
        print(f"  {r['subject']}: {r['ch_cnt']} chapters, {r['q_cnt']} questions")

conn.close()
