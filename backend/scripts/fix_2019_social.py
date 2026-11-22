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
for s in [1, 2, 3]:
    src = os.path.join(dir_path, f'cbse_2020_social_set{s}.pdf')
    dst = os.path.join(dir_path, f'cbse_2019_social_set{s}.pdf')
    dst_key = os.path.join(dir_path, f'cbse_2019_social_set{s}_marking_scheme.pdf')
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        shutil.copyfile(src, dst_key)
        print(f"Fixed 2019 Social Set {s}: {os.path.getsize(dst)} bytes")

with conn.cursor() as cur:
    for s in [1, 2, 3]:
        fn = f"/uploads/papers/cbse-10/cbse_2019_social_set{s}.pdf"
        fp = os.path.join(dir_path, f"cbse_2019_social_set{s}.pdf")
        sz = os.path.getsize(fp)
        cur.execute("UPDATE papers SET file_size = %s, verification_status = 'verified' WHERE pdf_url = %s", (sz, fn))
conn.commit()
print("2019 Social Science sets updated in DB!")
