import urllib.request
import json

res = urllib.request.urlopen('http://127.0.0.1:5000/exams/').read()
exams = json.loads(res)['exams']
print('Total exams on API:', len(exams))
for e in exams:
    slug = e['slug']
    cat_res = urllib.request.urlopen(f'http://127.0.0.1:5000/exams/{slug}').read()
    cats = json.loads(cat_res)['exam']['categories']
    papers_res = urllib.request.urlopen(f'http://127.0.0.1:5000/papers/?exam={slug}').read()
    papers = json.loads(papers_res)['papers']
    print(f"\nExam: {e['name']} ({slug}) -> {len(cats)} categories, {len(papers)} papers")
    if papers:
        sample = papers[0]
        print(f"   Sample paper: {sample['title']} ({sample['year']})")
        print(f"   Source: {sample.get('source_name')} | URL: {sample.get('source_url')}")
        print(f"   Local PDF: {sample.get('pdf_url')} | Size: {sample.get('file_size')} bytes")
