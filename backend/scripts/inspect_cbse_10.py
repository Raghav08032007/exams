import pymysql.cursors
import json

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

print("--- PAPERS IN CLASS 10 BY SUBJECT ---")
cur.execute("""
    SELECT s.name, count(*) as count, min(p.year) as min_y, max(p.year) as max_y
    FROM papers p
    JOIN paper_subjects ps ON p.id = ps.paper_id
    JOIN subjects s ON ps.subject_id = s.id
    JOIN exam_categories ec ON p.exam_category_id = ec.id
    WHERE ec.slug LIKE '%10%' OR ec.name LIKE '%10%'
    GROUP BY s.name
    ORDER BY count DESC
""")
for row in cur.fetchall():
    print(f"  {row['name']}: {row['count']} papers (Years: {row['min_y']} - {row['max_y']})")

print("\n--- CHAPTERS IN DATABASE ---")
cur.execute("""
    SELECT standard_level, subject_id, s.name as subject_name, count(*) as chapter_count
    FROM chapters c
    JOIN subjects s ON c.subject_id = s.id
    GROUP BY standard_level, subject_id, s.name
    ORDER BY standard_level, s.name
""")
for row in cur.fetchall():
    print(f"  {row['standard_level']} - {row['subject_name']}: {row['chapter_count']} chapters")

print("\n--- CHAPTER QUESTIONS IN DATABASE ---")
cur.execute("""
    SELECT s.name as subject_name, count(cq.id) as question_count
    FROM chapter_questions cq
    JOIN chapters c ON cq.chapter_id = c.id
    JOIN subjects s ON c.subject_id = s.id
    GROUP BY s.name
""")
for row in cur.fetchall():
    print(f"  {row['subject_name']}: {row['question_count']} questions")

conn.close()
