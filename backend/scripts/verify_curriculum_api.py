import urllib.request
import json

endpoints = [
    "http://127.0.0.1:5000/curriculum/github-stats",
    "http://127.0.0.1:5000/curriculum/class-10/cbse-10",
    "http://127.0.0.1:5000/curriculum/upsc/prelims",
    "http://127.0.0.1:5000/papers?exam=class-10&category=cbse-10&per_page=5"
]

for ep in endpoints:
    try:
        with urllib.request.urlopen(ep, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            print(f"✓ OK {resp.status}: {ep}")
            if "total_papers_in_system" in data:
                print(f"  Papers in DB: {data['total_papers_in_system']}, GitHub synced: {data['github_synchronized_papers']}, Textbooks: {data['textbooks_indexed']}")
            elif "curricula" in data:
                print(f"  Found {len(data['curricula'])} curricula. Sample: {data['curricula'][0]['curriculum_title'][:60]}")
            elif "papers" in data:
                print(f"  Found {len(data['papers'])} papers. Sample: {data['papers'][0]['title'][:60]} | Source: {data['papers'][0]['source_name']}")
    except Exception as e:
        print(f"✗ FAIL {ep}: {e}")
