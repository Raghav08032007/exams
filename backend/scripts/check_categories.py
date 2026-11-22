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
    cur.execute("SHOW TABLES")
    print("Tables:", [list(r.values())[0] for r in cur.fetchall()])

    cur.execute("DESCRIBE exam_categories")
    print("=== EXAM_CATEGORIES COLUMNS ===", [r['Field'] for r in cur.fetchall()])

    cur.execute("SELECT * FROM exam_categories")
    cats = cur.fetchall()
    print("=== EXAM_CATEGORIES ===")
    for c in cats:
        print(c)

    cur.execute("SELECT * FROM subjects")
    subs = cur.fetchall()
    print("=== SUBJECTS ===")
    for s in subs:
        print(s)

conn.close()
