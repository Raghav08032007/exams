import os, sys, pymysql.cursors

conn = pymysql.connect(
    host="localhost", user="root", password="261008", database="examvault",
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, name, slug FROM exams")
    exams = cur.fetchall()
    print("EXAMS:")
    for e in exams:
        cur.execute("SELECT id, name, slug FROM exam_categories WHERE exam_id = %s", (e["id"],))
        cats = cur.fetchall()
        print(f"[{e['id']}] {e['name']} ({e['slug']}):")
        for c in cats:
            print(f"   -> Cat [{c['id']}] {c['name']} ({c['slug']})")

    cur.execute("SELECT id, name, slug FROM subjects ORDER BY name")
    subjs = cur.fetchall()
    print(f"\nTOTAL SUBJECTS: {len(subjs)}")
    for s in subjs[:15]:
        print(f"   - [{s['id']}] {s['name']} ({s['slug']})")
