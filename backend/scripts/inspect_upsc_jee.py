import pymysql

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='261008', database='examvault', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT id, title, year, pdf_url
        FROM papers
        WHERE exam_category_id IN (SELECT id FROM exam_categories WHERE exam_id IN (SELECT id FROM exams WHERE slug IN ('upsc', 'jee')))
        ORDER BY year DESC
    """)
    rows = cur.fetchall()
    print(f"Total UPSC + JEE papers: {len(rows)}")
    for r in rows[:15]:
        print(f" {r['id']} | {r['year']} | {r['title']} | {r['pdf_url']}")

conn.close()
