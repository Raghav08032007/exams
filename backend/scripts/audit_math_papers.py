import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.id, p.year, p.title, p.pdf_url, p.file_size, p.verification_status, c.slug as cat_slug, p.has_answer_key, p.answer_key_pdf_url
            FROM papers p
            JOIN categories c ON p.category_id = c.id
            WHERE c.slug IN ('cbse-10', 'tn-sslc')
              AND (p.title LIKE '%math%' OR p.subject LIKE '%math%')
            ORDER BY p.year DESC, p.id ASC
        """)
        rows = cur.fetchall()
        print(f"Total Math papers found: {len(rows)}")
        years = sorted(list(set(r['year'] for r in rows)), reverse=True)
        print("Years present:", years)
        
        missing_files = []
        broken_urls = []
        
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        
        for r in rows:
            url = r['pdf_url'] or ''
            if url.startswith('/uploads/'):
                rel = url[len('/uploads/'):].replace('/', os.sep)
                full_path = os.path.join(upload_dir, rel)
                if not os.path.exists(full_path):
                    missing_files.append((r['id'], r['year'], r['title'], url))
                else:
                    sz = os.path.getsize(full_path)
                    if sz < 1000:
                        missing_files.append((r['id'], r['year'], r['title'], f"size {sz}b: {url}"))
            elif not url.startswith('http'):
                broken_urls.append((r['id'], r['year'], r['title'], url))

        print(f"Missing or tiny (<1KB) local files: {len(missing_files)}")
        for m in missing_files[:20]:
            print("  Missing:", m)
        
        print(f"Broken non-http non-upload URLs: {len(broken_urls)}")
        for b in broken_urls[:20]:
            print("  Broken:", b)

        by_cat_year = {}
        for r in rows:
            k = (r['cat_slug'], r['year'])
            by_cat_year[k] = by_cat_year.get(k, 0) + 1

        print("\nBreakdown by Category and Year:")
        for (cat, yr), count in sorted(by_cat_year.items(), key=lambda x: (x[0][0], -x[0][1])):
            print(f"  {cat} | {yr}: {count} papers")
