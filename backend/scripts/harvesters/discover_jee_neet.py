import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def check_page(url, label):
    print(f"\n--- Checking {label} ({url}) ---")
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')
        # find pdf links or drive links or cdn links
        pdf_links = re.findall(r'href=[\'"]([^\'"]+?\.pdf(?:\?[^\'"]*)?)[\'"]', html, re.I)
        drive_links = re.findall(r'href=[\'"]([^\'"]*(?:drive\.google|cloudfront|amazonaws|cdn)[^\'"]*)[\'"]', html, re.I)
        all_links = set(pdf_links + drive_links)
        print(f"Found {len(all_links)} candidate links:")
        for l in sorted(all_links)[:10]:
            print(" ", l)
        return list(all_links)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

check_page("https://www.mathongo.com/jee-main-question-paper/2024-january-shift-wise-question-paper", "Mathongo JEE 2024")
check_page("https://jeemain.nta.ac.in", "NTA JEE Main")
check_page("https://neet.nta.nic.in", "NTA NEET")
check_page("https://www.selfstudys.com/books/jee-previous-year-paper", "Selfstudys JEE")
