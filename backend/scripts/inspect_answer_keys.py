import pymysql

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) AS total, SUM(has_answer_key) AS with_key FROM papers")
    row = cur.fetchone()
    print(f"Total papers: {row['total']} | Papers with answer key: {row['with_key']}")

    cur.execute("""
        SELECT e.name, COUNT(*) as total, SUM(p.has_answer_key) as with_key 
        FROM papers p 
        JOIN exam_categories ec ON p.exam_category_id = ec.id 
        JOIN exams e ON ec.exam_id = e.id 
        GROUP BY e.name
    """)
    for r in cur.fetchall():
        print(f" - {r['name']}: {r['with_key']}/{r['total']} have answer keys")

    cur.execute("""
        SELECT id, title, has_answer_key, answer_key_pdf_url, source_url
        FROM papers
        WHERE has_answer_key = 1
        LIMIT 10
    """)
    keys = cur.fetchall()
    print("\nSample papers with answer keys:")
    for k in keys:
        print(f" ID: {k['id']} | Title: {k['title'][:40]} | Key URL: {k['answer_key_pdf_url']}")

conn.close()
