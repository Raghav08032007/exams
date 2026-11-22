import os, sys, pymysql.cursors
sys.path.insert(0, os.path.abspath('backend'))
from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT e.slug as exam_slug, ec.slug as cat_slug, p.year, COUNT(*) as cnt 
        FROM papers p 
        JOIN exam_categories ec ON p.exam_category_id = ec.id 
        JOIN exams e ON ec.exam_id = e.id 
        GROUP BY e.slug, ec.slug, p.year 
        ORDER BY e.slug, ec.slug, p.year DESC
    ''')
    rows = cursor.fetchall()
    print(f"Total groupings: {len(rows)}")
    for r in rows:
        print(f"{r['exam_slug']:<10} | {str(r['cat_slug']):<15} | {r['year']:<5} | {r['cnt']} papers")

    cursor.execute("SELECT count(*) as total FROM papers")
    total = cursor.fetchone()['total']
    print(f"\nTotal papers in DB: {total}")
