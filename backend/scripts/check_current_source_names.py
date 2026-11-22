import pymysql.cursors

conn = pymysql.connect(
    host="localhost", user="root", password="261008", database="examvault",
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, title, year, pdf_url, source_name, source_url FROM papers LIMIT 10")
    rows = cur.fetchall()
    print("Sample current papers:")
    for r in rows:
        print(f"ID: {r['id']} | {r['title']} | {r['year']} | URL: {r['pdf_url'][:60]} | Source: {r['source_name']}")

    cur.execute("SELECT source_name, COUNT(*) as cnt FROM papers GROUP BY source_name")
    sources = cur.fetchall()
    print("\nPapers by source_name:")
    for s in sources:
        print(f" - {s['source_name']}: {s['cnt']}")
