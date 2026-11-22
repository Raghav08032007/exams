import os
import shutil
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

upload_dir = 'f:/exam/backend/uploads'

# 1. Fix CBSE 10 Math 2024 & 2022 specific files
math_2024_real = os.path.join(upload_dir, 'papers', 'cbse-10', 'cbse_2024_maths_set1.pdf')
math_2022_real = os.path.join(upload_dir, 'papers', 'cbse-10', 'cbse_2022_maths_set1.pdf')
math_2023_real = os.path.join(upload_dir, 'papers', 'cbse-10', 'cbse_2023_maths_set1.pdf')

targets = {
    'cbse_2024_maths_std_paper.pdf': math_2024_real,
    'cbse_2024_maths_basic_paper.pdf': math_2024_real,
    'cbse_2024_maths_set2.pdf': math_2024_real,
    'cbse_2024_maths_set3.pdf': math_2024_real,
    'cbse_2022_term2_maths.pdf': math_2022_real,
    'cbse_2023_maths_paper.pdf': math_2023_real,
}

for tgt_name, src_path in targets.items():
    tgt_path = os.path.join(upload_dir, 'papers', 'cbse-10', tgt_name)
    if os.path.exists(src_path):
        shutil.copyfile(src_path, tgt_path)
        print(f"Replaced {tgt_name} with {src_path} ({os.path.getsize(tgt_path)} bytes)")

# 2. Update database sizes
with conn.cursor() as cur:
    cur.execute("""
        SELECT id, pdf_url FROM papers WHERE pdf_url LIKE '/uploads/papers/cbse-10/%'
    """)
    rows = cur.fetchall()
    updated = 0
    for r in rows:
        rel = r['pdf_url'][len('/uploads/'):]
        fp = os.path.join(upload_dir, rel.replace('/', os.sep))
        if os.path.exists(fp):
            sz = os.path.getsize(fp)
            cur.execute("UPDATE papers SET file_size = %s WHERE id = %s", (sz, r['id']))
            updated += 1
    conn.commit()
    print(f"Updated file_size for {updated} CBSE-10 papers in DB")
