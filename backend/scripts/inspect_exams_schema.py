import pymysql.cursors

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

cur.execute("DESCRIBE exams")
print("EXAMS SCHEMA:")
for col in cur.fetchall():
    print(f"  {col['Field']} ({col['Type']})")

cur.execute("SELECT id, name, slug FROM exams")
print("\nALL EXAMS IN DB:")
for e in cur.fetchall():
    print(f"  [{e['id']}] {e['name']} ({e['slug']})")

conn.close()
