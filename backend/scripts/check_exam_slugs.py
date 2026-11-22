import pymysql, os
from dotenv import load_dotenv
from urllib.parse import urlparse
load_dotenv('f:/exam/backend/.env')
p = urlparse(os.getenv('DATABASE_URL'))
conn = pymysql.connect(host=p.hostname or 'localhost', port=p.port or 3306, user=p.username or 'root', password=p.password or '', database=p.path.lstrip('/') or 'examvault', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT ec.slug as cat_slug, e.slug as exam_slug, e.name as exam_name FROM exam_categories ec JOIN exams e ON ec.exam_id = e.id WHERE ec.slug IN ('cbse-10', 'tn-sslc')")
    for r in cur.fetchall():
        print(r)
