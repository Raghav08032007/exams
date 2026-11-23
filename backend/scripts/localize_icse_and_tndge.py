import os
import pymysql
import urllib.request
import urllib.parse
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

# 1. Localize ICSE (2630)
os.makedirs('f:/exam/backend/uploads/papers/icse-board', exist_ok=True)
with conn.cursor() as cur:
    cur.execute("SELECT id, pdf_url FROM papers WHERE exam_category_id = 2630 AND pdf_url LIKE 'http%'")
    icse_papers = cur.fetchall()

icse_updates = []
for p in icse_papers:
    fname = os.path.basename(p['pdf_url'])
    dest = os.path.abspath(f"f:/exam/backend/uploads/papers/icse-board/{fname}")
    rel = f"/uploads/papers/icse-board/{fname}"
    try:
        req = urllib.request.Request(p['pdf_url'], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            with open(dest, 'wb') as f:
                f.write(r.read())
        icse_updates.append((rel, p['id']))
    except Exception as e:
        print("ICSE error:", p['id'], e)

if icse_updates:
    with conn.cursor() as cur:
        cur.executemany("UPDATE papers SET pdf_url = %s WHERE id = %s", icse_updates)
    conn.commit()
    print(f"Updated {len(icse_updates)} ICSE papers to local!")

# 2. Localize or relink TN DGE (2626)
os.makedirs('f:/exam/backend/uploads/papers/tn-board', exist_ok=True)
with conn.cursor() as cur:
    cur.execute("SELECT id, pdf_url FROM papers WHERE exam_category_id = 2626 AND pdf_url LIKE 'http%'")
    tn_papers = cur.fetchall()

tn_updates = []
for p in tn_papers:
    fname = os.path.basename(p['pdf_url'])
    # check if already in tn-hsc
    hsc_path = os.path.abspath(f"f:/exam/backend/uploads/papers/tn-hsc/{fname}")
    if os.path.exists(hsc_path):
        tn_updates.append((f"/uploads/papers/tn-hsc/{fname}", p['id']))
    else:
        # download to tn-board
        dest = os.path.abspath(f"f:/exam/backend/uploads/papers/tn-board/{fname}")
        rel = f"/uploads/papers/tn-board/{fname}"
        try:
            req = urllib.request.Request(p['pdf_url'], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
                if len(data) > 1000:
                    with open(dest, 'wb') as f:
                        f.write(data)
                    tn_updates.append((rel, p['id']))
        except Exception as e:
            pass

if tn_updates:
    with conn.cursor() as cur:
        cur.executemany("UPDATE papers SET pdf_url = %s WHERE id = %s", tn_updates)
    conn.commit()
    print(f"Updated {len(tn_updates)} TN DGE papers to local!")

# Clean any remaining broken remote records in 2626
with conn.cursor() as cur:
    cur.execute("SELECT id FROM papers WHERE exam_category_id = 2626 AND pdf_url LIKE 'http%'")
    unfixed = [r['id'] for r in cur.fetchall()]
    if unfixed:
        fmt = ','.join(['%s'] * len(unfixed))
        cur.execute(f"DELETE FROM paper_subjects WHERE paper_id IN ({fmt})", unfixed)
        cur.execute(f"DELETE FROM user_notes WHERE paper_id IN ({fmt})", unfixed)
        cur.execute(f"DELETE FROM practice_attempts WHERE paper_id IN ({fmt})", unfixed)
        cur.execute(f"DELETE FROM bookmarks WHERE paper_id IN ({fmt})", unfixed)
        cur.execute(f"DELETE FROM papers WHERE id IN ({fmt})", unfixed)
        conn.commit()
        print(f"Purged {len(unfixed)} unresolvable TN DGE records.")
