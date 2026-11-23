import os, pymysql
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
    cur.execute("SELECT id, name, slug FROM exams")
    exams = cur.fetchall()
    print("=== EXAMS ===")
    for e in exams:
        print(f"ID {e['id']}: {e['name']} ({e['slug']})")

    cur.execute("SELECT ec.id, ec.name, ec.slug, e.name as exam_name FROM exam_categories ec JOIN exams e ON ec.exam_id = e.id")
    cats = cur.fetchall()
    print("\n=== CATEGORIES ===")
    for c in cats:
        print(f"ID {c['id']}: {c['name']} ({c['slug']}) -> {c['exam_name']}")
