import urllib.request
import urllib.parse
import json

base_url = 'http://127.0.0.1:5000'

tests = [
    ('All Subjects list', '/papers/subjects'),
    ('Mathematics papers', '/papers/?subject=Mathematics'),
    ('Physics papers', '/papers/?subject=Physics'),
    ('Chemistry papers', '/papers/?subject=Chemistry'),
    ('Biology papers', '/papers/?subject=Biology'),
    ('General Studies papers', '/papers/?subject=' + urllib.parse.quote('General Studies')),
    ('CSAT papers', '/papers/?subject=CSAT'),
    ('Class 10 Science papers', '/papers/?exam=class-10&subject=Science'),
    ('UPSC Mains Essay papers', '/papers/?exam=upsc&subject=Essay'),
    ('Class 12 Economics papers', '/papers/?exam=class-12&subject=Economics'),
]

for label, path in tests:
    req = urllib.request.Request(base_url + path, headers={'User-Agent': 'Mozilla/5.0'})
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    if 'subjects' in res:
        subjs = res['subjects']
        top_names = [s['name'] for s in subjs[:5]]
        print(f"{label:<28}: {len(subjs)} subjects found (top: {top_names})")
    elif 'papers' in res:
        total = res['pagination']['total']
        sample_title = res['papers'][0]['title'] if res['papers'] else 'None'
        print(f"{label:<28}: {total} papers found (Sample: {sample_title[:45]}...)")
