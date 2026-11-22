import urllib.request
import json

base_url = "http://127.0.0.1:5000"

def check(endpoint, label):
    try:
        url = f"{base_url}{endpoint}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        print(f"✓ {label} ({endpoint}): SUCCESS -> {type(data)} keys: {list(data.keys()) if isinstance(data, dict) else len(data)}")
        return data
    except Exception as e:
        print(f"✗ {label} ({endpoint}): FAILED -> {e}")
        return None

print("Testing Live API Endpoints...")
d_chapters = check("/chapters/?standard=Class+10", "Chapters Class 10")
if d_chapters and 'chapters' in d_chapters:
    print(f"  Count: {len(d_chapters['chapters'])} chapters")
    if d_chapters['chapters']:
        ch1 = d_chapters['chapters'][0]
        print(f"  Sample Chapter: Ch {ch1['chapter_number']} {ch1['chapter_title']} ({ch1['subject_name']})")
        # Test detail
        d_ch_detail = check(f"/chapters/{ch1['id']}", f"Chapter Detail ID {ch1['id']}")
        if d_ch_detail and 'chapter' in d_ch_detail:
            q_cnt = len(d_ch_detail['chapter'].get('questions', []))
            print(f"    Questions in chapter: {q_cnt}")

d_papers = check("/papers/?per_page=5", "Papers API")
if d_papers and 'pagination' in d_papers:
    print(f"  Pagination keys: {d_papers['pagination']}")

d_sources = check("/sources/", "Sources API")
if d_sources and 'sources' in d_sources:
    print(f"  Total sources indexed: {len(d_sources['sources'])}")
    cbse_sources = [s for s in d_sources['sources'] if 'boards10' in s['url'].lower() or 'cbse' in s['name'].lower()]
    print(f"  CBSE / Boards10 sources: {[s['name'] for s in cbse_sources]}")
