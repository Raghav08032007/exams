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
    for name in ['Mathematics', 'Science', 'Social Science', 'English', 'Tamil']:
        cur.execute("SELECT id, name FROM subjects WHERE name LIKE %s", (f"%{name}%",))
        print(f"=== Matches for {name} ===")
        for r in cur.fetchall():
            print(f"  id: {r['id']}, name: {r['name']}")

conn.close()
