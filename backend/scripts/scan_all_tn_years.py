import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_url = "https://www.educationobserver.com/forum/"

# All known thread IDs or URLs for each year
year_sources = {
    2024: [
        "https://www.educationobserver.com/forum/showthread.php?tid=29233", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=29236", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=29240", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=29379", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=31632", # Social
    ],
    2023: [
        "https://www.educationobserver.com/forum/showthread.php?tid=28098", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=28108", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=28116", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=28127", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=28128", # Social
    ],
    2022: [
        "https://www.educationobserver.com/forum/showthread.php?tid=27586", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=27585", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=27589", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=27587", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=27588", # Social
    ],
    2021: [
        "https://www.educationobserver.com/forum/showthread.php?tid=24295", # Tamil
        "https://www.educationobserver.com/forum/showthread.php?tid=24297", # English
        "https://www.educationobserver.com/forum/showthread.php?tid=24293", # Maths
        "https://www.educationobserver.com/forum/showthread.php?tid=24296", # Science
        "https://www.educationobserver.com/forum/showthread.php?tid=24298", # Social
    ],
    2020: [
        "https://www.educationobserver.com/forum/showthread.php?tid=24295",
        "https://www.educationobserver.com/forum/showthread.php?tid=24297",
        "https://www.educationobserver.com/forum/showthread.php?tid=24293",
        "https://www.educationobserver.com/forum/showthread.php?tid=24296",
        "https://www.educationobserver.com/forum/showthread.php?tid=24298",
    ],
    2019: [
        "https://www.educationobserver.com/forum/showthread.php?tid=23265",
    ],
    2018: [
        "https://www.educationobserver.com/forum/showthread.php?tid=21844",
    ],
    2017: [
        "https://www.educationobserver.com/forum/showthread.php?tid=21102",
    ],
    2016: [
        "https://www.educationobserver.com/forum/showthread.php?tid=21110",
    ],
    2015: [
        "https://www.educationobserver.com/forum/showthread.php?tid=18002",
    ]
}

def scan_year(year, urls):
    print(f"\n==================== SCANNING {year} ====================")
    found = []
    for u in urls:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            # Find attachments
            atts = re.findall(r'href=[\'"]([^\'"]*attachment\.php\?aid=(\d+))[^\'"]*[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
            for href, aid, text in atts:
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                full_href = href if href.startswith('http') else base_url + href
                found.append((clean_text, full_href, aid))
        except Exception as e:
            print(f"Error {u}: {e}")
    
    print(f"Total attachments for {year}: {len(found)}")
    for t, l, aid in found[:10]:
        print(f"  [{aid}] {t}")
    return found

all_year_data = {}
for yr, url_list in year_sources.items():
    all_year_data[yr] = scan_year(yr, url_list)
