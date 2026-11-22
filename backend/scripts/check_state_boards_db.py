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
    cur.execute("""
        SELECT ec.name, ec.slug, COUNT(p.id) as cnt
        FROM exam_categories ec
        LEFT JOIN papers p ON p.exam_category_id = ec.id
        WHERE ec.exam_id = 1120 OR ec.id IN (67, 1801, 2630)
        GROUP BY ec.id, ec.name, ec.slug
        ORDER BY ec.name
    """)
    rows = cur.fetchall()
    print("=== STATE BOARDS INGESTED STATUS ===")
    for r in rows:
        print(f"  {r['name']} ({r['slug']}): {r['cnt']} papers")

conn.close()
