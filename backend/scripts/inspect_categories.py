import pymysql.cursors

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

print("--- EXAM CATEGORIES ---")
cur.execute("SELECT id, exam_id, name, slug FROM exam_categories")
for row in cur.fetchall():
    print(row)

print("\n--- PAPERS BY EXAM CATEGORY ---")
cur.execute("""
    SELECT ec.id, ec.name, ec.slug, count(p.id) as count
    FROM exam_categories ec
    LEFT JOIN papers p ON ec.id = p.exam_category_id
    GROUP BY ec.id, ec.name, ec.slug
    HAVING count > 0
    ORDER BY count DESC
""")
for row in cur.fetchall():
    print(f"ID {row['id']}: {row['name']} ({row['slug']}) -> {row['count']} papers")

conn.close()
