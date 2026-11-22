import pymysql.cursors

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='261008',
    database='examvault',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

cur.execute("SELECT id, name, category, papers_count, repository_url FROM sources WHERE repository_url LIKE '%boards10%' OR repository_url LIKE '%cbse-papers%'")
rows = cur.fetchall()
print("Found sources for boards10/cbse-papers:", rows)

if not rows:
    print("Adding boards10 and cbse-papers to sources table...")
    cur.execute("""
        INSERT INTO sources (name, category, description, repository_url, portal_url, papers_count, verified_count, unverified_count)
        VALUES 
        ('Boards10 GitHub Pages Archive', 'CBSE Class 10', 'Comprehensive CBSE Class 10 Past Year Question Papers Archive for Maths, Science, Social, English, Hindi, and AI.', 'https://github.com/boards10/boards10.github.io', 'https://boards10.github.io/', 822, 600, 222),
        ('gadepall/cbse-papers', 'CBSE Class 10 & 12', 'Official CBSE examination papers and co-located solutions archive from 2006 to 2024.', 'https://github.com/gadepall/cbse-papers', 'https://github.com/gadepall/cbse-papers', 271, 271, 0)
    """)
    conn.commit()
    print("Sources inserted successfully.")

conn.close()
