import pymysql.cursors

conn = pymysql.connect(
    host="localhost", user="root", password="261008", database="examvault",
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, name, slug FROM exams ORDER BY id")
    exams = cur.fetchall()
    print("CURRENT EXAMS:")
    for e in exams:
        cur.execute("SELECT id, name, slug FROM exam_categories WHERE exam_id = %s", (e["id"],))
        cats = cur.fetchall()
        print(f"[{e['id']}] {e['name']} ({e['slug']}): {len(cats)} categories")
        for c in cats:
            print(f"    - Cat [{c['id']}] {c['name']} ({c['slug']})")
