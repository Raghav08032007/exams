import pymysql.cursors

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

print("--- ALL SUBJECTS IN PAPERS ---")
cur.execute("""
    SELECT s.id, s.name, count(ps.paper_id) as paper_count
    FROM subjects s
    LEFT JOIN paper_subjects ps ON s.id = ps.subject_id
    GROUP BY s.id, s.name
    ORDER BY paper_count DESC
""")
all_subjects = cur.fetchall()
print(f"Total subjects: {len(all_subjects)}")
for s in all_subjects[:35]:
    print(f"  [{s['id']}] {s['name']}: {s['paper_count']} papers")

print("\n--- SUBJECTS IN CHAPTERS VS MISSING ---")
cur.execute("""
    SELECT DISTINCT s.id, s.name, c.standard_level, c.exam_slug
    FROM chapters c
    JOIN subjects s ON c.subject_id = s.id
""")
chapter_subjects = cur.fetchall()
print(f"Distinct subject-standard pairs with chapters: {len(chapter_subjects)}")
for cs in chapter_subjects:
    print(f"  {cs['standard_level']} ({cs['exam_slug']}): {cs['name']}")

print("\n--- EXAMS & EDUCATION SECTORS ---")
cur.execute("SELECT id, name, slug, exam_type FROM exams")
for e in cur.fetchall():
    print(f"Exam [{e['id']}]: {e['name']} ({e['slug']}) Type: {e.get('exam_type')}")

conn.close()
