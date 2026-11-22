import pymysql.cursors

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

print("--- TAMIL PAPERS IN DATABASE ---")
cur.execute("""
    SELECT p.id, p.title, p.year, p.session, ec.name as category, p.pdf_url
    FROM papers p
    JOIN paper_subjects ps ON p.id = ps.paper_id
    JOIN subjects s ON ps.subject_id = s.id
    JOIN exam_categories ec ON p.exam_category_id = ec.id
    WHERE s.name LIKE '%Tamil%' OR p.title LIKE '%Tamil%'
""")
for row in cur.fetchall():
    print(f"[{row['category']}] ({row['year']}) {row['title']} -> {row['pdf_url'][:70]}...")

print("\n--- SAMPLE PAPERS IN CBSE 10 ---")
cur.execute("""
    SELECT p.id, p.title, p.year, p.session, s.name as subject_name
    FROM papers p
    JOIN paper_subjects ps ON p.id = ps.paper_id
    JOIN subjects s ON ps.subject_id = s.id
    WHERE p.exam_category_id = 64
    LIMIT 20
""")
for row in cur.fetchall():
    print(f"[{row['year']}] ({row['subject_name']}) {row['title']}")

conn.close()
