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
    cur.execute("""
        SELECT p.id, p.title, p.source_url, p.pdf_url, p.has_answer_key, p.answer_key_pdf_url
        FROM papers p
        JOIN exam_categories ec ON p.exam_category_id = ec.id
        WHERE ec.slug LIKE '%cbse%'
        LIMIT 10
    """)
    for r in cur.fetchall():
        print(r)

conn.close()
