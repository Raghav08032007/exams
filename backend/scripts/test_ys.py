import urllib.request, json

url = 'http://localhost:5000/exams/class-10/categories/cbse-10/year-sessions'
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode())
    years = [ys['year'] for ys in data.get('year_sessions', [])]
    unique_years = sorted(list(set(years)), reverse=True)
    print("cbse-10 year-sessions unique years:", unique_years)

url2 = 'http://localhost:5000/exams/class-10/categories/tn-sslc/year-sessions'
with urllib.request.urlopen(url2) as resp:
    data2 = json.loads(resp.read().decode())
    years2 = [ys['year'] for ys in data2.get('year_sessions', [])]
    unique_years2 = sorted(list(set(years2)), reverse=True)
    print("tn-sslc year-sessions unique years:", unique_years2)
