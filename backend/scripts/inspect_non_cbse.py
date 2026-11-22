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
    for exam in ['upsc', 'jee', 'neet', 'tnpsc']:
        cur.execute("""
            SELECT p.id, p.title, p.year, p.has_answer_key, p.answer_key_pdf_url, p.pdf_url
            FROM papers p
            JOIN exam_categories ec ON p.exam_category_id = ec.id
            JOIN exams e ON ec.exam_id = e.id
            WHERE e.slug = %s
            ORDER BY p.year DESC, p.title ASC
            LIMIT 5
        """, (exam,))
        rows = cur.fetchall()
        print(f"\n--- {exam.upper()} (Sample 5) ---")
        for r in rows:
            print(f" ID: {r['id']} | {r['year']} | has_key: {r['has_answer_key']} | key_url: {r['answer_key_pdf_url']} | Title: {r['title'][:45]}")

conn.close()
