import urllib.request
import json

base_url = "http://127.0.0.1:5000"

def test_endpoint(path, name):
    try:
        url = f"{base_url}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            print(f"✓ {name}: {len(data.get('chapters', []))} chapters returned.")
            return data
    except Exception as e:
        print(f"✗ {name}: Failed -> {e}")

print("--- TESTING BACKEND 4-TIER CHAPTER FILTERS ---")
test_endpoint("/chapters/", "All Chapters")
test_endpoint("/chapters/?education=school", "Education: School")
test_endpoint("/chapters/?domain=languages", "Domain: Languages (Tamil, Hindi, English, Sanskrit, Arabic)")
test_endpoint("/chapters/?domain=tech_commerce", "Domain: Tech & Commerce (IT, CS, Accountancy)")
test_endpoint("/chapters/?q=real+numbers", "Search Query: Real Numbers")
test_endpoint("/chapters/?q=tamil", "Search Query: Tamil")
