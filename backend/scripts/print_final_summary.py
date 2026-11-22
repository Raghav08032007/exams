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
    cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) as verified_cnt FROM papers")
    counts = cur.fetchone()
    print("=== PAPERS TOTAL & VERIFIED ===")
    print(f"Total Papers: {counts['total']}")
    print(f"Verified Papers: {counts['verified_cnt']}")

    cur.execute("""
        SELECT ec.name, COUNT(*) as cnt
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        GROUP BY ec.name
        ORDER BY cnt DESC
    """)
    cats = cur.fetchall()
    print("\n=== TOP CATEGORIES ===")
    for c in cats[:15]:
        print(f"  {c['name']}: {c['cnt']} papers")

conn.close()
