import urllib.request
import json
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
}

url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        tree = data.get("tree", [])
        print(f"Total entries: {len(tree)}")
        
        # Filter for PDFs
        pdfs = [item["path"] for item in tree if item["path"].lower().endswith(".pdf")]
        print(f"Total PDFs: {len(pdfs)}")
        
        # Categorize
        categories = {
            "CBSE_10": [],
            "CBSE_12": [],
            "CBSE_Other": [],
            "JEE": [],
            "NEET": [],
            "UPSC": [],
            "Tamil_Nadu": [],
            "Other_Boards": []
        }
        
        for p in pdfs:
            lower = p.lower()
            if "cbse" in lower or "central_board" in lower:
                if "10" in lower or "class_10" in lower or "class-10" in lower or "x/" in lower or "class 10" in lower:
                    categories["CBSE_10"].append(p)
                elif "12" in lower or "class_12" in lower or "class-12" in lower or "xii/" in lower or "class 12" in lower:
                    categories["CBSE_12"].append(p)
                else:
                    categories["CBSE_Other"].append(p)
            elif "jee" in lower:
                categories["JEE"].append(p)
            elif "neet" in lower:
                categories["NEET"].append(p)
            elif "upsc" in lower or "civil" in lower:
                categories["UPSC"].append(p)
            elif "tamil" in lower or "tn" in lower:
                categories["Tamil_Nadu"].append(p)
            else:
                categories["Other_Boards"].append(p)
                
        for cat, items in categories.items():
            print(f"\n--- {cat}: {len(items)} PDFs ---")
            for item in items[:8]:
                print("  ", item)
                
except Exception as e:
    print("Error:", e)
