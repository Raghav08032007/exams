import urllib.request
import json

base_url = "http://127.0.0.1:5000"

def test():
    # 1. Textbooks standards
    req = urllib.request.urlopen(f"{base_url}/textbooks/standards")
    data = json.loads(req.read().decode())
    print("Textbooks Standards count:", len(data.get("standards", [])))

    # 2. Textbooks filtered
    req = urllib.request.urlopen(f"{base_url}/textbooks/?standard=Class%2010")
    data = json.loads(req.read().decode())
    print("Class 10 Textbooks count:", len(data.get("textbooks", [])))

    # 3. List papers
    req = urllib.request.urlopen(f"{base_url}/papers/?exam=class-10&per_page=5")
    data = json.loads(req.read().decode())
    papers = data.get("papers", [])
    print(f"Fetched {len(papers)} Class 10 papers")
    if papers:
        first = papers[0]
        print(f"Paper 1 ID: {first['id']}, Title: {first['title']}, HasKey: {first['has_answer_key']}, Attached Textbooks: {len(first.get('textbooks', []))}")
        
        # 4. Get individual paper
        req2 = urllib.request.urlopen(f"{base_url}/papers/{first['id']}")
        data2 = json.loads(req2.read().decode())
        p2 = data2.get("paper", {})
        print(f"Get Paper {first['id']}: Attached textbooks: {len(p2.get('textbooks', []))}")
        for tb in p2.get("textbooks", []):
            print(f"   -> {tb['board']} {tb['standard_level']} - {tb['title']}")

if __name__ == "__main__":
    test()
