import urllib.request
import json

# 1. Papers with answer key
url_with_key = 'http://127.0.0.1:5000/papers/?has_answer_key=1&per_page=5'
resp1 = json.loads(urllib.request.urlopen(url_with_key).read().decode())
print(f"Total papers with answer keys: {resp1['pagination']['total']}")
for p in resp1['papers']:
    print(f" - ID: {p['id']} | Title: {p['title'][:35]} | has_key: {p['has_answer_key']} | key_url: {p['answer_key_pdf_url']}")

# 2. Papers without answer key
url_no_key = 'http://127.0.0.1:5000/papers/?has_answer_key=0&per_page=5'
resp2 = json.loads(urllib.request.urlopen(url_no_key).read().decode())
print(f"\nTotal papers without answer keys: {resp2['pagination']['total']}")
for p in resp2['papers']:
    print(f" - ID: {p['id']} | Title: {p['title'][:35]} | has_key: {p['has_answer_key']}")

# 3. Test single paper detail
test_id = resp1['papers'][0]['id']
resp3 = json.loads(urllib.request.urlopen(f'http://127.0.0.1:5000/papers/{test_id}').read().decode())
paper = resp3['paper']
print(f"\nPaper {test_id} Detail Verification:")
print(f" Title: {paper['title']}")
print(f" Question Paper URL: {paper['pdf_url']}")
print(f" Answer Key URL:     {paper['answer_key_pdf_url']}")
print(f" Has Answer Key:     {paper['has_answer_key']}")
