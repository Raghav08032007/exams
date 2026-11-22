import urllib.request
import urllib.parse
import json

def test_query(cat, sub, yr):
    url = f"http://localhost:5000/papers?exam=class-10&category={cat}&subject={urllib.parse.quote(sub)}&year={yr}"
    try:
        with urllib.request.urlopen(url) as r:
            res = json.loads(r.read())
            papers = res.get('papers', [])
            print(f"[{cat}] {sub} {yr} -> {len(papers)} papers found")
            if papers:
                p = papers[0]
                title = p.get('title', '')[:50]
                url_str = p.get('pdf_url', '')
                sz = p.get('file_size')
                print(f"    First: {title}... ({url_str}) [size: {sz}]")
    except Exception as e:
        print(f"[{cat}] {sub} {yr} -> Error: {e}")

print("=== VERIFYING LIVE API QUERIES ===")
for sub in ['Mathematics', 'Science', 'Social Science', 'English', 'Tamil']:
    test_query('cbse-10', sub, 2024)
    test_query('cbse-10', sub, 2018)
    test_query('tn-sslc', sub, 2024)
    test_query('tn-sslc', sub, 2018)
