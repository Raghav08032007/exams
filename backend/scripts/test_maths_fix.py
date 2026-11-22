import urllib.request, urllib.parse, json

for subj in ['Mathematics', 'Maths']:
    url = f"http://localhost:5000/papers?exam=class-10&category=cbse-10&subject={urllib.parse.quote(subj)}&per_page=10"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
        print(f"Subj: '{subj}' -> total in top-level: {data.get('total')}, total_pages: {data.get('total_pages')}, pagination: {data.get('pagination')}")
