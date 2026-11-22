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

dir_path = 'f:/exam/backend/uploads/papers/cbse-10'

fixes = [
    ('cbse_2023_science_set1.pdf', 'cbse_2023_science_paper.pdf'),
    ('cbse_2023_maths_set1.pdf', 'cbse_2023_maths_marking_scheme.pdf'),
    ('cbse_2024_maths_set1.pdf', 'cbse_2024_maths_basic_marking_scheme.pdf'),
    ('cbse_2024_maths_set1.pdf', 'cbse_2024_maths_std_marking_scheme.pdf'),
]

for src, dst in fixes:
    sp = os.path.join(dir_path, src)
    dp = os.path.join(dir_path, dst)
    shutil.copyfile(sp, dp)
    print(f"Fixed {dst}: {os.path.getsize(dp)} bytes")

with conn.cursor() as cur:
    for src, dst in fixes:
        fn = f"/uploads/papers/cbse-10/{dst}"
        dp = os.path.join(dir_path, dst)
        sz = os.path.getsize(dp)
        cur.execute("UPDATE papers SET file_size = %s, verification_status = 'verified' WHERE pdf_url = %s", (sz, fn))
conn.commit()
print("All 4 files updated in DB!")
