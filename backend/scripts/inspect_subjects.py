import pymysql.cursors

conn = pymysql.connect(
    host='localhost', user='root', password='261008',
    database='examvault', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute('''
        SELECT s.id, s.name, COUNT(ps.paper_id) as paper_count 
        FROM subjects s 
        LEFT JOIN paper_subjects ps ON s.id = ps.subject_id 
        GROUP BY s.id, s.name 
        ORDER BY paper_count DESC
    ''')
    rows = cur.fetchall()
    print(f"Total subjects in DB: {len(rows)}")
    for r in rows:
        print(f"  {r['name']:<30} -> {r['paper_count']} papers")

    # Check papers with 0 subjects
    cur.execute('''
        SELECT count(*) as unmapped FROM papers p 
        LEFT JOIN paper_subjects ps ON p.id = ps.paper_id 
        WHERE ps.subject_id IS NULL
    ''')
    unmapped = cur.fetchone()['unmapped']
    print(f"\nPapers without any subjects: {unmapped}")

conn.close()
