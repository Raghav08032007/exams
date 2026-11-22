import pymysql.cursors

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

cur.execute("""
    SELECT c.id, c.standard_level, s.name as subject_name, c.chapter_number, c.chapter_title
    FROM chapters c
    JOIN subjects s ON c.subject_id = s.id
    ORDER BY c.standard_level, s.name, c.chapter_number
""")
for row in cur.fetchall():
    print(f"[{row['standard_level']}] {row['subject_name']} - Ch {row['chapter_number']}: {row['chapter_title']}")

conn.close()
