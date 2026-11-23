import urllib.request
import re

boards_to_check = {
    'Tamil_Nadu': ['2015', '2016', '2017', '2018', '2020'],
    'Maharashtra': ['2014', '2015', '2016', '2017', '2018', '2019', '2020'],
    'Uttar_Pradesh': ['2015', '2016', '2017', '2018', '2019', '2020'],
    'Kerala': ['2015', '2016', '2017', '2018', '2019', '2020'],
    'West_Bengal': ['2015', '2016', '2017', '2018', '2020'],
    'Andhra_Pradesh': ['2015', '2016', '2017', '2018', '2020']
}

for b, years in boards_to_check.items():
    print(f"\n--- Board: {b} ---")
    for yr in years:
        u = f"https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/{b}/{yr}"
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                html = r.read().decode('utf-8', errors='ignore')
                files = re.findall(rf'/Shabber10/ALL-PYQ-Papers/blob/main/Boards/{b}/{yr}/([^"/?#]+)', html)
                pdf_files = [f for f in files if f.endswith('.pdf')]
                print(f"  {yr}: {len(pdf_files)} PDFs (sample: {pdf_files[:3]})")
        except Exception as e:
            print(f"  {yr}: Error {e}")
