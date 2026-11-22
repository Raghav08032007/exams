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
    cur.execute("DESCRIBE exams")
    print("=== EXAMS COLUMNS ===", [r['Field'] for r in cur.fetchall()])

    cur.execute("DESCRIBE subjects")
    print("=== SUBJECTS COLUMNS ===", [r['Field'] for r in cur.fetchall()])

    cur.execute("DESCRIBE papers")
    print("=== PAPERS COLUMNS ===", [r['Field'] for r in cur.fetchall()])

    cur.execute("SELECT id, name, code FROM subjects")
    subs = cur.fetchall()
    print(f"\nSubjects ({len(subs)} total):")
    for s in subs:
        print(f"  {s['id']}: {s['name']} (code: {s['code']})")

conn.close()
