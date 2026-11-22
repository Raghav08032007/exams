import os
import sys
import json
import re
import urllib.request
import urllib.parse
import pymysql.cursors

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "261008")
DB_NAME = os.getenv("MYSQL_DB", "examvault")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def get_or_create_subject(cur, name: str) -> int:
    cur.execute("SELECT id FROM subjects WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
    return cur.lastrowid

# ── STAGE 1: INGEST BOARDS10.GITHUB.IO PAPERS ──────────────────────────────
def ingest_boards10_papers(cur, cat_10_id):
    print("=" * 60)
    print("STAGE 1: Fetching and Ingesting papers from boards10.github.io...")
    url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/data.js"
    req = urllib.request.Request(url, headers=HEADERS)
    content = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')

    raw_json = re.sub(r'^\s*const\s+DATA\s*=\s*', '', content).rstrip(';\n ')
    data = json.loads(raw_json)

    subj_mapping = {
        "english": "English",
        "math": "Mathematics",
        "science": "Science",
        "social": "Social Science",
        "hindi_a": "Hindi",
        "hindi_b": "Hindi",
        "ait": "Information Technology",
        "arabic": "Arabic"
    }

    inserted = 0
    updated = 0

    for raw_subj, paper_list in data.items():
        standard_subj_name = subj_mapping.get(raw_subj, raw_subj.title())
        subj_id = get_or_create_subject(cur, standard_subj_name)

        for p in paper_list:
            file_rel = p.get("file", "")
            if not file_rel:
                continue
            year = int(p.get("year", 2024))
            set_num = str(p.get("set", "")).strip()
            exam_type = p.get("exam", "Main")
            raw_url = f"https://boards10.github.io/{file_rel}"
            gh_url = f"https://github.com/boards10/boards10.github.io/blob/main/{file_rel}"
            file_size = p.get("size", 2500000)

            set_str = f"Set {set_num}" if set_num else "Main"
            session = f"{exam_type} ({set_str})"
            title = f"CBSE Class 10 {year} — {standard_subj_name} Question Paper ({set_str})"

            status = 'unverified' if year >= 2025 else 'verified'

            cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND title = %s", (cat_10_id, title))
            existing = cur.fetchone()

            if existing:
                cur.execute("""
                    UPDATE papers SET
                        year = %s,
                        session = %s,
                        pdf_url = %s,
                        file_size = %s,
                        source_name = 'GitHub: boards10.github.io (CBSE 10 Hub)',
                        source_url = %s,
                        verification_status = %s
                    WHERE id = %s
                """, (year, session, raw_url, file_size, gh_url, status, existing["id"]))
                paper_id = existing["id"]
                updated += 1
            else:
                cur.execute("""
                    INSERT INTO papers (
                        exam_category_id, year, session, title, language, pdf_url,
                        file_size, has_answer_key, source_url, source_name,
                        paper_type, verification_status, download_count
                    ) VALUES (
                        %s, %s, %s, %s, 'English', %s,
                        %s, 0, %s, 'GitHub: boards10.github.io (CBSE 10 Hub)',
                        'original', %s, 0
                    )
                """, (cat_10_id, year, session, title, raw_url, file_size, gh_url, status))
                paper_id = cur.lastrowid
                inserted += 1

            cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (paper_id, subj_id))

    print(f"✓ boards10.github.io: Ingested {inserted} new papers, updated {updated} existing.")

# ── STAGE 2: INGEST GADEPALL/CBSE-PAPERS ────────────────────────────────────
def ingest_gadepall_papers(cur, cat_10_id, cat_12_id):
    print("=" * 60)
    print("STAGE 2: Fetching and Ingesting papers from gadepall/cbse-papers...")
    url = "https://api.github.com/repos/gadepall/cbse-papers/git/trees/main?recursive=1"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode())
        tree = data.get("tree", [])

    pdfs = [x for x in tree if x["path"].lower().endswith(".pdf")]
    
    # Map solution files
    sol_map = {}
    for x in pdfs:
        p = x["path"]
        if "solution" in p.lower():
            base = p.lower().replace("/solutions/main.pdf", "").replace("/solutions/cbse_grade_10_paper.pdf", "")
            sol_map[base] = f"https://raw.githubusercontent.com/gadepall/cbse-papers/main/{urllib.parse.quote(p)}"

    math_subj_id = get_or_create_subject(cur, "Mathematics")
    inserted = 0
    updated = 0

    for x in pdfs:
        path = x["path"]
        if "solution" in path.lower() or "/figs/" in path.lower():
            continue

        raw_url = f"https://raw.githubusercontent.com/gadepall/cbse-papers/main/{urllib.parse.quote(path)}"
        gh_url = f"https://github.com/gadepall/cbse-papers/blob/main/{urllib.parse.quote(path)}"
        file_size = x.get("size", 1800000)

        # Detect year and class
        y_m = re.search(r"(\d{4})", path)
        year = int(y_m.group(1)) if y_m else 2018

        is_c12 = "/12/" in path or "12th" in path
        cat_id = cat_12_id if is_c12 else cat_10_id
        class_name = "Class 12" if is_c12 else "Class 10"

        # Check for co-located solution key
        base_dir = "/".join(path.split("/")[:-1]).lower()
        ak_url = sol_map.get(base_dir)
        has_ak = 1 if ak_url else 0

        title = f"CBSE {class_name} {year} — Mathematics Question Paper & LaTeX Proofs"

        cur.execute("SELECT id FROM papers WHERE exam_category_id = %s AND title = %s", (cat_id, title))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE papers SET
                    pdf_url = %s,
                    file_size = %s,
                    source_name = 'GitHub: gadepall/cbse-papers',
                    source_url = %s,
                    has_answer_key = CASE WHEN %s = 1 THEN 1 ELSE has_answer_key END,
                    answer_key_pdf_url = CASE WHEN %s IS NOT NULL THEN %s ELSE answer_key_pdf_url END,
                    verification_status = 'verified'
                WHERE id = %s
            """, (raw_url, file_size, gh_url, has_ak, ak_url, ak_url, existing["id"]))
            paper_id = existing["id"]
            updated += 1
        else:
            cur.execute("""
                INSERT INTO papers (
                    exam_category_id, year, session, title, language, pdf_url,
                    file_size, has_answer_key, answer_key_pdf_url, source_url, source_name,
                    paper_type, verification_status, download_count
                ) VALUES (
                    %s, %s, 'Annual Board', %s, 'English', %s,
                    %s, %s, %s, %s, 'GitHub: gadepall/cbse-papers',
                    'original', 'verified', 0
                )
            """, (cat_id, year, title, raw_url, file_size, has_ak, ak_url, gh_url))
            paper_id = cur.lastrowid
            inserted += 1

        cur.execute("INSERT IGNORE INTO paper_subjects (paper_id, subject_id) VALUES (%s, %s)", (paper_id, math_subj_id))

    print(f"✓ gadepall/cbse-papers: Ingested {inserted} new papers, updated {updated} existing.")

# ── STAGE 3: COMPREHENSIVE CHAPTERS & CHAPTER QUESTIONS FOR 10TH SUBJECTS ──
def seed_all_10th_subject_lessons(cur):
    print("=" * 60)
    print("STAGE 3: Populating 10th Lessons & Chapter-wise Questions (Maths, Science, Social, English, Tamil)...")

    # Subjects
    sub_math = get_or_create_subject(cur, "Mathematics")
    sub_sci  = get_or_create_subject(cur, "Science")
    sub_soc  = get_or_create_subject(cur, "Social Science")
    sub_eng  = get_or_create_subject(cur, "English")
    sub_tam  = get_or_create_subject(cur, "Tamil")

    lessons_dataset = [
        # ═══════════════════════════════════════════════════════════════
        # 1. MATHEMATICS (Class 10 CBSE)
        # ═══════════════════════════════════════════════════════════════
        {
            "subject_id": sub_math,
            "chapter_num": 1,
            "title": "Real Numbers",
            "notes": "Fundamental Theorem of Arithmetic states that every composite number can be uniquely expressed as a product of primes, apart from the order in which the prime factors occur. LCM(a, b) * HCF(a, b) = a * b. Irrationality of sqrt(2), sqrt(3), sqrt(5) proved by contradiction using p/q form where p and q are co-prime.",
            "weightage": 6,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "If HCF(306, 657) = 9, find LCM(306, 657).",
                    "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2024,
                    "src": "CBSE Board 2024 (Set 1)",
                    "ans": "Using LCM(a,b) = (a * b) / HCF(a,b) = (306 * 657) / 9 = 34 * 657 = 22,338."
                },
                {
                    "q": "Prove that 3 + 2√5 is an irrational number, given that √5 is irrational.",
                    "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2023,
                    "src": "CBSE Board 2023 (Set 2)",
                    "ans": "Assume on the contrary that 3 + 2√5 is rational = a/b where a,b are co-prime, b≠0. Then 2√5 = a/b - 3 = (a-3b)/b => √5 = (a-3b)/(2b). Since a,b are integers, (a-3b)/(2b) is rational, meaning √5 is rational. This contradicts the fact that √5 is irrational. Hence 3 + 2√5 is irrational."
                },
                {
                    "q": "Case Study: An Army contingent of 616 members is to march behind an army band of 32 members in a Republic Day parade. What is the maximum number of columns in which they can march?",
                    "type": "Case Study", "marks": 4, "diff": "Medium", "year": 2022,
                    "src": "CBSE Board 2022 (Term 1 / Set 1)",
                    "ans": "The maximum number of columns is the HCF(616, 32). Using Euclid/Prime Factorization: 616 = 32 * 19 + 8; 32 = 8 * 4 + 0. Therefore HCF(616, 32) = 8 columns."
                }
            ]
        },
        {
            "subject_id": sub_math,
            "chapter_num": 2,
            "title": "Polynomials",
            "notes": "A quadratic polynomial ax^2 + bx + c has at most 2 zeroes. Sum of zeroes alpha + beta = -b/a; Product of zeroes alpha * beta = c/a. Polynomial is formed as k[x^2 - (alpha + beta)x + (alpha * beta)]. Zeroes correspond geometrically to x-intercepts of the graph.",
            "weightage": 5,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "If one zero of the quadratic polynomial x^2 + 3x + k is 2, then the value of k is:\n(A) 10 (B) -10 (C) -7 (D) -2",
                    "type": "MCQ", "marks": 1, "diff": "Easy", "year": 2024,
                    "src": "CBSE Board 2024 (Set 2)",
                    "ans": "Since 2 is a zero, P(2) = 0 => (2)^2 + 3(2) + k = 0 => 4 + 6 + k = 0 => k = -10. Correct option is (B)."
                },
                {
                    "q": "Find the zeroes of the quadratic polynomial 6x^2 - 3 - 7x and verify the relationship between the zeroes and the coefficients.",
                    "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2023,
                    "src": "CBSE Board 2023 (Set 3)",
                    "ans": "Rearrange: 6x^2 - 7x - 3 = 6x^2 - 9x + 2x - 3 = 3x(2x-3) + 1(2x-3) = (2x-3)(3x+1) = 0. Zeroes are alpha = 3/2, beta = -1/3. Sum = 3/2 - 1/3 = 7/6 = -(-7)/6 = -b/a. Product = (3/2)(-1/3) = -3/6 = c/a. Verified."
                }
            ]
        },
        {
            "subject_id": sub_math,
            "chapter_num": 3,
            "title": "Pair of Linear Equations in Two Variables",
            "notes": "General form: a1*x + b1*y + c1 = 0 and a2*x + b2*y + c2 = 0. Conditions: Unique solution (intersecting) if a1/a2 != b1/b2; Infinitely many (coincident) if a1/a2 = b1/b2 = c1/c2; No solution (parallel) if a1/a2 = b1/b2 != c1/c2. Solved via Substitution or Elimination.",
            "weightage": 7,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "Solve the pair of equations: 2x + 3y = 11 and 2x - 4y = -24, and hence find the value of 'm' for which y = mx + 3.",
                    "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2024,
                    "src": "CBSE Board 2024 (Set 1)",
                    "ans": "Subtracting (2) from (1): 7y = 35 => y = 5. Substituting in (1): 2x + 15 = 11 => 2x = -4 => x = -2. Now y = mx + 3 => 5 = m(-2) + 3 => 2m = -2 => m = -1."
                },
                {
                    "q": "5 years ago, Nuri was thrice as old as Sonu. Ten years later, Nuri will be twice as old as Sonu. How old are Nuri and Sonu?",
                    "type": "Long Answer", "marks": 5, "diff": "Hard", "year": 2020,
                    "src": "CBSE Board 2020 (Standard)",
                    "ans": "Let Nuri's age = x, Sonu's age = y. 5 yrs ago: (x-5) = 3(y-5) => x - 3y = -10. 10 yrs later: (x+10) = 2(y+10) => x - 2y = 10. Subtracting gives y = 20. Then x = 50. Nuri is 50 years old and Sonu is 20 years old."
                }
            ]
        },
        {
            "subject_id": sub_math,
            "chapter_num": 6,
            "title": "Triangles",
            "notes": "Basic Proportionality Theorem (Thales Theorem): If a line is drawn parallel to one side of a triangle intersecting the other two sides, then it divides the two sides in the same ratio. Similarity criteria: AAA/AA, SSS, SAS. Ratio of areas of similar triangles = square of ratio of corresponding sides.",
            "weightage": 8,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "State and prove Basic Proportionality Theorem (BPT / Thales Theorem).",
                    "type": "Long Answer", "marks": 5, "diff": "Hard", "year": 2023,
                    "src": "CBSE Board 2023 (Set 1)",
                    "ans": "Given triangle ABC, line DE || BC intersecting AB at D and AC at E. Draw DM perpendicular to AC and EN perpendicular to AB. Join BE and CD. Area(ADE) = 1/2 * AD * EN = 1/2 * AE * DM. Area(BDE) = 1/2 * DB * EN. Area(DEC) = 1/2 * EC * DM. Since triangles BDE and DEC are on the same base DE between the same parallels DE and BC, Area(BDE) = Area(DEC). Hence Area(ADE)/Area(BDE) = Area(ADE)/Area(DEC) => AD/DB = AE/EC. Proved."
                }
            ]
        },
        {
            "subject_id": sub_math,
            "chapter_num": 8,
            "title": "Introduction to Trigonometry",
            "notes": "Trigonometric ratios defined on right-angled triangles: sin theta = opp/hyp, cos theta = adj/hyp, tan theta = opp/adj. Fundamental identities: sin^2 theta + cos^2 theta = 1; 1 + tan^2 theta = sec^2 theta; 1 + cot^2 theta = cosec^2 theta. Specific angles: 0, 30, 45, 60, 90 degrees.",
            "weightage": 8,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "Prove that: (sin theta - 2 sin^3 theta) / (2 cos^3 theta - cos theta) = tan theta.",
                    "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2024,
                    "src": "CBSE Board 2024 (Set 3)",
                    "ans": "LHS = sin theta (1 - 2 sin^2 theta) / [cos theta (2 cos^2 theta - 1)]. Note that 1 - 2 sin^2 theta = cos^2 theta - sin^2 theta = 2 cos^2 theta - 1. Thus LHS = (sin theta / cos theta) * 1 = tan theta = RHS. Proved."
                }
            ]
        },

        # ═══════════════════════════════════════════════════════════════
        # 2. SCIENCE (Class 10 CBSE)
        # ═══════════════════════════════════════════════════════════════
        {
            "subject_id": sub_sci,
            "chapter_num": 1,
            "title": "Chemical Reactions and Equations",
            "notes": "Chemical equation represents reactants transforming into products with conservation of mass. Types: Combination, Decomposition (thermal, electrolytic, photochemical), Displacement, Double displacement (precipitation), Oxidation-Reduction (Redox). Corrosion and rancidity prevention.",
            "weightage": 6,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Science.pdf",
            "questions": [
                {
                    "q": "Identify the substance oxidised and the substance reduced in the following reaction:\nMnO2 + 4HCl -> MnCl2 + 2H2O + Cl2",
                    "type": "Short Answer", "marks": 2, "diff": "Medium", "year": 2024,
                    "src": "CBSE Board 2024 (Set 1)",
                    "ans": "HCl is oxidised to Cl2 (loss of hydrogen). MnO2 is reduced to MnCl2 (loss of oxygen). MnO2 acts as the oxidising agent and HCl acts as the reducing agent."
                },
                {
                    "q": "Why is respiration considered an exothermic reaction? Explain with a balanced chemical equation.",
                    "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2023,
                    "src": "CBSE Board 2023 (Set 2)",
                    "ans": "During respiration, glucose combines with oxygen in the cells of our body and breaks down into carbon dioxide and water, releasing energy in the form of ATP. Chemical equation: C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy."
                }
            ]
        },
        {
            "subject_id": sub_sci,
            "chapter_num": 5,
            "title": "Life Processes",
            "notes": "Maintenance processes essential for sustaining life: Nutrition (Autotrophic photosynthesis equation 6CO2 + 12H2O -> C6H12O6 + 6O2 + 6H2O; Heterotrophic holozoic), Respiration (Glycolysis in cytoplasm to pyruvate; aerobic in mitochondria, anaerobic in yeast/muscles), Transportation (Double circulation in human heart, xylem/phloem in plants), Excretion (Nephron filtration, selective reabsorption, tubular secretion).",
            "weightage": 9,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Science.pdf",
            "questions": [
                {
                    "q": "Describe the process of double circulation in human beings. Why is it necessary to separate oxygenated and deoxygenated blood in mammals and birds?",
                    "type": "Long Answer", "marks": 5, "diff": "Hard", "year": 2024,
                    "src": "CBSE Board 2024 (Set 2)",
                    "ans": "Double circulation consists of (i) Pulmonary circulation: Deoxygenated blood from right ventricle reaches lungs via pulmonary artery, gets oxygenated and returns to left atrium via pulmonary veins. (ii) Systemic circulation: Oxygenated blood from left ventricle pumped into aorta to body tissues and deoxygenated blood collected by vena cava returns to right atrium. Separation is necessary to maintain high metabolic rate and constant body temperature (warm-blooded animals)."
                },
                {
                    "q": "Draw a neat labelled diagram of a Nephron and explain the three steps of urine formation.",
                    "type": "Long Answer", "marks": 5, "diff": "Hard", "year": 2023,
                    "src": "CBSE Board 2023 (Set 1)",
                    "ans": "Three steps: 1. Ultrafiltration: High pressure in glomerulus forces water, glucose, amino acids, urea into Bowman's capsule. 2. Selective Reabsorption: Useful substances (glucose, amino acids, salts, major water) reabsorbed along tubular nephron. 3. Tubular Secretion: Excess ions (K+, H+, drugs) secreted into tubule to form final urine flowing into collecting duct."
                }
            ]
        },
        {
            "subject_id": sub_sci,
            "chapter_num": 11,
            "title": "Electricity",
            "notes": "Electric current I = Q/t. Potential difference V = W/Q. Ohm's Law V = I*R at constant temperature. Factors affecting resistance: length, cross-sectional area (R = rho * l / A), material and temperature. Series combination: Rs = R1 + R2 + R3; Parallel combination: 1/Rp = 1/R1 + 1/R2 + 1/R3. Joule's law of heating H = I^2 * R * t. Power P = V*I = I^2*R = V^2/R.",
            "weightage": 7,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Science.pdf",
            "questions": [
                {
                    "q": "An electric lamp of resistance 20 ohms and a conductor of 4 ohms resistance are connected in series to a 6 V battery. Calculate: (a) Total resistance of circuit (b) Current flowing through circuit (c) Potential difference across the electric lamp.",
                    "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2024,
                    "src": "CBSE Board 2024 (Set 1)",
                    "ans": "(a) Total resistance R = 20 + 4 = 24 ohms. (b) Current I = V / R = 6 / 24 = 0.25 A. (c) Potential difference across lamp V_lamp = I * R_lamp = 0.25 * 20 = 5 V."
                }
            ]
        },

        # ═══════════════════════════════════════════════════════════════
        # 3. SOCIAL SCIENCE (Class 10 CBSE)
        # ═══════════════════════════════════════════════════════════════
        {
            "subject_id": sub_soc,
            "chapter_num": 1,
            "title": "The Rise of Nationalism in Europe",
            "notes": "Frederic Sorrieu's utopian vision (1848). French Revolution proclaimed that the people would constitute the nation. Napoleonic Code (Civil Code of 1804) abolished feudal privileges, established equality before law. Liberalism and Zollverein customs union (1834). Unification of Germany under Bismarck (1871) and Italy under Cavour, Garibaldi, and Victor Emmanuel II (1861). Balkan crisis leading to World War I.",
            "weightage": 6,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Indian-and-Contemporary-World-2.pdf",
            "questions": [
                {
                    "q": "Explain any three provisions of the Civil Code of 1804 (Napoleonic Code) introduced by Napoleon in France.",
                    "type": "Short Answer", "marks": 3, "diff": "Easy", "year": 2024,
                    "src": "CBSE Board 2024 (Set 2)",
                    "ans": "1. Abolished all privileges based on birth. 2. Established equality before the law and secured the right to property. 3. Simplified administrative divisions, abolished the feudal system, and freed peasants from serfdom and manorial dues."
                },
                {
                    "q": "Describe the process of Unification of Germany.",
                    "type": "Long Answer", "marks": 5, "diff": "Medium", "year": 2023,
                    "src": "CBSE Board 2023 (Set 1)",
                    "ans": "1. Nationalist feelings were strong among middle-class Germans who tried to unite German confederation in 1848 at Frankfurt Parliament. 2. Prussia took leadership under Chief Minister Otto von Bismarck (Architect of Unification). 3. Bismarck followed the policy of 'Blood and Iron' with Prussian army and bureaucracy. 4. Three wars over 7 years against Austria, Denmark, and France ended in Prussian victory. 5. In January 1871, Prussian King William I was proclaimed German Emperor at the Hall of Mirrors in Versailles."
                }
            ]
        },
        {
            "subject_id": sub_soc,
            "chapter_num": 2,
            "title": "Nationalism in India",
            "notes": "Impact of World War I: defense expenditure, taxes, forced recruitment, influenza epidemic. Mahatma Gandhi's return in 1915 and Satyagraha experiments (Champaran, Kheda, Ahmedabad). Rowlatt Act (1919) and Jallianwala Bagh massacre (13 April 1919). Khilafat and Non-Cooperation Movement (1920-1922), Chauri Chaura incident. Simon Commission (1928), Lahore Congress & Purna Swaraj (1929). Salt March to Dandi (1930) and Civil Disobedience Movement. Gandhi-Irwin Pact and Poona Pact (1932).",
            "weightage": 7,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Indian-and-Contemporary-World-2.pdf",
            "questions": [
                {
                    "q": "Why did Mahatma Gandhi decide to withdraw the Non-Cooperation Movement in February 1922?",
                    "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2024,
                    "src": "CBSE Board 2024 (Set 3)",
                    "ans": "Gandhi withdrew the Non-Cooperation Movement due to the violent incident at Chauri Chaura (Gorakhpur, UP) where a peaceful demonstration turned violent and peasants set fire to a police station, killing 22 policemen. Gandhi felt the movement was turning violent and satyagrahis needed proper training in non-violence."
                },
                {
                    "q": "Explain the significance of the Salt March (Dandi March) undertaken by Mahatma Gandhi in 1930.",
                    "type": "Long Answer", "marks": 5, "diff": "Medium", "year": 2022,
                    "src": "CBSE Board 2022 (Term 2)",
                    "ans": "1. Marked the beginning of the Civil Disobedience Movement. 2. Salt was chosen as a unifying symbol consumed by rich and poor alike; government monopoly and tax were oppressive. 3. Gandhi walked 240 miles from Sabarmati to Dandi with 78 volunteers over 24 days. 4. On 6 April 1930, he broke the salt law by boiling sea water. 5. Thousands broke salt laws across India, boycotted foreign cloth, and refused to pay revenue."
                }
            ]
        },

        # ═══════════════════════════════════════════════════════════════
        # 4. ENGLISH (Class 10 CBSE)
        # ═══════════════════════════════════════════════════════════════
        {
            "subject_id": sub_eng,
            "chapter_num": 1,
            "title": "A Letter to God (First Flight)",
            "notes": "Written by G.L. Fuentes. Story of Lencho, a dedicated Mexican peasant farmer whose cornfield is destroyed by a devastating hailstorm. With unshakable faith in God, he writes a letter asking for 100 pesos. The compassionate postmaster and post office employees collect 70 pesos to help him. Lencho calls them a 'bunch of crooks' suspecting they stole the remaining 30 pesos, highlighting ironical human distrust despite extreme faith.",
            "weightage": 5,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "Why did Lencho write a letter to God? Who received the letter and what was their reaction?",
                    "type": "Short Answer", "marks": 3, "diff": "Easy", "year": 2024,
                    "src": "CBSE Board 2024 (Set 1)",
                    "ans": "Lencho wrote to God asking for 100 pesos because a hailstorm had completely destroyed his ripe cornfields, threatening his family with starvation. The postmaster received the letter, first laughed at the address, but was soon moved by Lencho's extraordinary faith and decided to collect money to help him."
                },
                {
                    "q": "What is the irony in the end of the story 'A Letter to God'?",
                    "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2023,
                    "src": "CBSE Board 2023 (Set 2)",
                    "ans": "The irony is that the postmaster and his employees contributed out of their own salaries to send Lencho 70 pesos. However, Lencho blamed these very benefactors, calling them 'a bunch of crooks', believing that God could not have made a mistake and the post office employees must have stolen the missing 30 pesos."
                }
            ]
        },
        {
            "subject_id": sub_eng,
            "chapter_num": 2,
            "title": "Nelson Mandela: Long Walk to Freedom",
            "notes": "Autobiographical excerpt from South Africa's first Black President inauguration on 10 May 1994 at the Union Buildings amphitheatre in Pretoria. Describes apartheid, the rainbow gathering of world leaders, Mandela's twin obligations (to family and to people), and courage defined not as the absence of fear, but the triumph over it.",
            "weightage": 6,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "What 'twin obligations' does Nelson Mandela mention in his speech?",
                    "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2024,
                    "src": "CBSE Board 2024 (Set 2)",
                    "ans": "Mandela mentions that every man has twin obligations: first, to his family, parents, wife and children; second, to his people, community and country. Under apartheid, a man of color in South Africa was punished and isolated if he attempted to fulfill both obligations."
                }
            ]
        },

        # ═══════════════════════════════════════════════════════════════
        # 5. TAMIL (Class 10 CBSE & State Board SSLC)
        # ═══════════════════════════════════════════════════════════════
        {
            "subject_id": sub_tam,
            "chapter_num": 1,
            "title": "இயல் 1: அன்னை மொழியே & தமிழ்ச்சொல் வளம்",
            "notes": "பாவலரேறு பெருஞ்சித்திரனாரின் கணிச்சாறு தொகுப்பிலிருந்து எடுக்கப்பட்ட 'அன்னை மொழியே'. தமிழ் மொழியின் பழமை, சிறப்பு, நற்றினை உள்ளிட்ட எட்டுத்தொகை, பத்துப்பாட்டு சிறப்புகள். தேவநேயப் பாவாணரின் 'தமிழ்ச்சொல் வளம்' - அடிவகை, கிளைப்பிரிவுகள், காய்ந்த இலை, கொழுந்து, பூவின் நிலைகள் உள்ளிட்ட நுட்பமான தமிழ்ச்சொற்கள்.",
            "weightage": 8,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "'அன்னை மொழியே' பாடலில் பெருஞ்சித்திரனார் தமிழை எவ்வாறு வாழ்த்துகிறார்?",
                    "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2024,
                    "src": "10th Tamil Board Exam 2024 (Set 1)",
                    "ans": "சின்னஞ்சிறு அழகாய் வீற்றிருக்கும் அன்னை மொழியே! செழுமையான பழமைக்கும் பழமையாய் உருவான நறுங்கனியே! பாண்டிய மன்னனின் மகளே! திருக்குறளின் பெரும் பெருமைக்குரியவளே! எட்டுத்தொகையே, பத்துப்பாட்டே, பதினெண்கீழ்க்கணக்கே, சிலப்பதிகாரமே, மணிமேகலையே என உன்னைத் தலைவணங்கி வாழ்த்துகிறோம் என வாழ்த்துகிறார்."
                },
                {
                    "q": "தாவரத்தின் பிஞ்சு வகைகளுக்கு வழங்கும் தமிழ்ச்சொற்களை எழுதுக.",
                    "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2023,
                    "src": "10th Tamil Board Exam 2023 (Set 2)",
                    "ans": "பூம்பிஞ்சு (பூவோடு கூடிய பிஞ்சு), பிஞ்சு (இளம் காய்), வடு (மாம்பிஞ்சு), மூசு (பலாப்பிஞ்சு), கவ்வை (எள்ளுப்பிஞ்சு), குறும்பை (தென்னை, பனைப் பிஞ்சு), இளநீர் (முற்றாத தேங்காய்)."
                }
            ]
        },
        {
            "subject_id": sub_tam,
            "chapter_num": 4,
            "title": "இயல் 4: செயற்கை நுண்ணறிவு & நானிலம்",
            "notes": "நவீன யுகத்தில் செயற்கை நுண்ணறிவின் (Artificial Intelligence) ஆதிக்கம், பயன்பாடுகள், மெய்நிகர் உதவியாளர், ஒளிப்படக் கருவி, தானியங்கி ஊர்திகள். மனித மூளையின் சிந்தனை ஆற்றலை இயந்திரங்களுக்கு வழங்குதல். அறிவியல் வளர்ச்சியோடு தமிழ் மொழியை இணைக்கும் வழிமுறைகள்.",
            "weightage": 7,
            "pdf_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
            "questions": [
                {
                    "q": "செயற்கை நுண்ணறிவு இன்றைய மனித வாழ்க்கையில் எவ்வாறு பயன்படுகிறது என்பதை விளக்குக.",
                    "type": "Long Answer", "marks": 5, "diff": "Medium", "year": 2024,
                    "src": "10th Tamil Board Exam 2024 (Set 1)",
                    "ans": "1. மெய்நிகர் உதவியாளர்கள் (Siri, Alexa) குரல் வழிக் கட்டளைகளை நிறைவேற்றுகின்றன. 2. தானியங்கி கார்கள் மற்றும் போக்குவரத்து நெரிசல் கண்காணிப்பு. 3. மருத்துவத்துறையில் நோய் கண்டறிதல் மற்றும் அறுவை சிகிச்சைக்குத் துணைபுரிதல். 4. வணிகத் தளங்களில் நுகர்வோர் விருப்பங்களை அறிந்து பரிந்துரைத்தல். 5. கல்வித்துறையில் தனிப்பயனாக்கப்பட்ட கற்றல் சூழலை உருவாக்குதல்."
                }
            ]
        }
    ]

    ch_inserted = 0
    q_inserted = 0

    for l in lessons_dataset:
        cur.execute("""
            SELECT id FROM chapters
            WHERE exam_slug = 'class-10' AND subject_id = %s AND chapter_number = %s
        """, (l["subject_id"], l["chapter_num"]))
        existing_ch = cur.fetchone()

        if existing_ch:
            ch_id = existing_ch["id"]
            cur.execute("""
                UPDATE chapters SET
                    chapter_title = %s,
                    summary_notes = %s,
                    marks_weightage = %s,
                    textbook_chapter_url = %s
                WHERE id = %s
            """, (l["title"], l["notes"], l["weightage"], l["pdf_url"], ch_id))
        else:
            cur.execute("""
                INSERT INTO chapters (
                    exam_slug, standard_level, subject_id, board,
                    chapter_number, chapter_title, textbook_chapter_url,
                    summary_notes, marks_weightage
                ) VALUES (
                    'class-10', 'Class 10', %s, 'CBSE',
                    %s, %s, %s,
                    %s, %s
                )
            """, (l["subject_id"], l["chapter_num"], l["title"], l["pdf_url"], l["notes"], l["weightage"]))
            ch_id = cur.lastrowid
            ch_inserted += 1

        # Insert / Update Questions
        for q in l["questions"]:
            cur.execute("""
                SELECT id FROM chapter_questions
                WHERE chapter_id = %s AND question_text = %s
            """, (ch_id, q["q"]))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO chapter_questions (
                        chapter_id, question_text, question_type, marks,
                        answer_explanation, source_publication, difficulty, year
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """, (
                    ch_id, q["q"], q["type"], q["marks"],
                    q["ans"], q["src"], q["diff"], q["year"]
                ))
                q_inserted += 1

    print(f"✓ Populated 10th Lessons: {ch_inserted} new chapters created/updated, {q_inserted} new chapter questions added.")

def main():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = conn.cursor()

    # Get CBSE Class 10 and 12 category IDs
    cur.execute("SELECT id FROM exam_categories WHERE slug = 'cbse-10'")
    cat_10 = cur.fetchone()
    cat_10_id = cat_10["id"] if cat_10 else 64

    cur.execute("SELECT id FROM exam_categories WHERE slug = 'cbse-12'")
    cat_12 = cur.fetchone()
    cat_12_id = cat_12["id"] if cat_12 else 69

    ingest_boards10_papers(cur, cat_10_id)
    ingest_gadepall_papers(cur, cat_10_id, cat_12_id)
    seed_all_10th_subject_lessons(cur)

    conn.commit()

    # Total counts verification
    cur.execute("SELECT COUNT(*) AS total_papers FROM papers")
    tp = cur.fetchone()["total_papers"]
    cur.execute("SELECT COUNT(*) AS total_ch FROM chapters")
    tc = cur.fetchone()["total_ch"]
    cur.execute("SELECT COUNT(*) AS total_q FROM chapter_questions")
    tq = cur.fetchone()["total_q"]

    print("=" * 60)
    print("ALL NEW SOURCES, BOARDS10, GADEPALL, AND 10TH LESSONS INGESTED SUCCESSFULLY!")
    print(f"Total Papers in Database:           {tp}")
    print(f"Total Chapters / Lessons in Database: {tc}")
    print(f"Total Chapter Questions in Database: {tq}")
    print("=" * 60)

    conn.close()

if __name__ == "__main__":
    main()
