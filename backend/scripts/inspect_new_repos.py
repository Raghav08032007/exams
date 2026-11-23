import urllib.request
import re

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error {url}: {e}")
        return ""

# Math 12 in gadepall
html_math12 = fetch("https://github.com/gadepall/cbse-papers/tree/main/papers/math/12")
years = re.findall(r'/gadepall/cbse-papers/tree/main/papers/math/12/([^"/?#]+)', html_math12)
print("Years in gadepall math/12:", sorted(list(set(years))))

# Pratishthaspn/CBSE
html_prat = fetch("https://github.com/Pratishthaspn/CBSE")
folders_prat = re.findall(r'/Pratishthaspn/CBSE/tree/main/([^"/?#]+)', html_prat)
print("Folders in Pratishthaspn/CBSE:", sorted(list(set(folders_prat))))

# yashitanamdeo/class12_study_materials
html_yash = fetch("https://github.com/yashitanamdeo/class12_study_materials")
folders_yash = re.findall(r'/yashitanamdeo/class12_study_materials/tree/main/([^"/?#]+)', html_yash)
print("Folders in yashita class12:", sorted(list(set(folders_yash))))
