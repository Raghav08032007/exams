import urllib.request, urllib.parse, json

for yr in range(2015, 2027):
    url = f"http://localhost:5000/papers?exam=class-10&category=cbse-10&subject=Mathematics&year={yr}&per_page=50"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            total = data.get('total', 0)
            papers = data.get('papers', [])
            print(f"Year {yr} + Mathematics: total in json: {total}, papers returned: {len(papers)}")
            if papers:
                print(f"   Sample paper: ID {papers[0]['id']} - {papers[0]['title']}")
    except Exception as e:
        print(f"Year {yr} -> error: {e}")
