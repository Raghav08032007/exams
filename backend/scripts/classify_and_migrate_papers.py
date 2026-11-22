"""
Classify and migrate papers to distinguish 'original' vs 'sample'.
Adds paper_type column to papers table if not present.
"""
import pymysql
import os

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "261008"),
    "database": os.environ.get("MYSQL_DATABASE", "examvault"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True
}

def migrate_and_classify():
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        # 1. Check if paper_type column exists
        cur.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'papers' AND COLUMN_NAME = 'paper_type'
        """, (DB_CONFIG["database"],))
        col = cur.fetchone()
        
        if not col:
            print("Adding 'paper_type' column to papers table...")
            cur.execute("""
                ALTER TABLE papers 
                ADD COLUMN paper_type VARCHAR(20) NOT NULL DEFAULT 'original',
                ADD INDEX ix_papers_paper_type (paper_type)
            """)
            print("Column added successfully.")
        else:
            print("'paper_type' column already exists.")

        # 2. Fetch all papers
        cur.execute("SELECT id, title, source_url, source_name FROM papers")
        papers = cur.fetchall()
        print(f"Total papers in database: {len(papers)}")

        sample_count = 0
        original_count = 0

        for p in papers:
            title_lower = (p["title"] or "").lower()
            source_lower = (p["source_url"] or "").lower()
            
            # Identify sample papers
            is_sample = False
            if "sample" in title_lower or "sqp" in title_lower or "/sqp/" in source_lower or "sample" in source_lower:
                is_sample = True
            
            p_type = "sample" if is_sample else "original"
            if is_sample:
                sample_count += 1
            else:
                original_count += 1

            cur.execute("UPDATE papers SET paper_type = %s WHERE id = %s", (p_type, p["id"]))

        print(f"Classification complete:")
        print(f" - Original Question Papers: {original_count}")
        print(f" - Official Sample Papers:   {sample_count}")

        # Show breakdown by exam
        cur.execute("""
            SELECT e.name AS exam_name, p.paper_type, COUNT(*) AS count
            FROM papers p
            JOIN exam_categories ec ON p.exam_category_id = ec.id
            JOIN exams e ON ec.exam_id = e.id
            GROUP BY e.name, p.paper_type
            ORDER BY e.name, p.paper_type
        """)
        breakdown = cur.fetchall()
        print("\nBreakdown by Exam and Paper Type:")
        for b in breakdown:
            print(f" - {b['exam_name']} [{b['paper_type']}]: {b['count']} papers")

    conn.close()

if __name__ == "__main__":
    migrate_and_classify()
