import os
import sys
import pymysql.cursors

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "261008")
DB_NAME = os.getenv("MYSQL_DB", "examvault")

def main():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cur:
        # Create sources table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                url VARCHAR(1000) NOT NULL,
                direct_repo_path VARCHAR(500),
                description TEXT,
                papers_count INT DEFAULT 0,
                status VARCHAR(50) DEFAULT 'Active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✓ Created or verified `sources` table")

        # Clear existing to re-seed cleanly
        cur.execute("TRUNCATE TABLE sources")

        sources_data = [
            # ── 1. GITHUB MAIN REPO & DEMO WEB APP ──
            {
                "name": "Shabber10/ALL-PYQ-Papers (Official GitHub Repository)",
                "category": "GitHub Open Source",
                "source_type": "git_repository",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers",
                "direct_repo_path": "/",
                "description": "Primary open-source Git archive with 42,159 files and 2,872 verified PDFs across Board, Entrance, Defence, and Civil Services exams.",
                "papers_count": 2872,
                "status": "Active & Synchronized"
            },
            {
                "name": "Boards10 CBSE Class 10 PYQ Papers Archive & Subject Hub",
                "category": "GitHub Open Source",
                "source_type": "git_repository",
                "url": "https://boards10.github.io/",
                "direct_repo_path": "https://github.com/boards10/boards10.github.io",
                "description": "Open-source CBSE Class 10 examination repository archiving 822 question papers across Mathematics, Science, Social Science, English, Hindi A/B, AI, and Arabic with set-wise categorization.",
                "papers_count": 822,
                "status": "Active & Synchronized"
            },
            {
                "name": "gadepall/cbse-papers (CBSE Past Papers & Solutions)",
                "category": "GitHub Open Source",
                "source_type": "git_repository",
                "url": "https://github.com/gadepall/cbse-papers",
                "direct_repo_path": "/",
                "description": "Public CBSE examination repository providing 271 question papers and co-located solutions from 2006 to 2024 for Class 10 and 12.",
                "papers_count": 271,
                "status": "Active & Synchronized"
            },
            {
                "name": "PYQs by Shabber — Netlify Web Application",
                "category": "Live Web Portal",
                "source_type": "web_application",
                "url": "https://pyqs-by-shabber.netlify.app",
                "direct_repo_path": "README.md",
                "description": "Live search and filter web application hosted on Netlify, referenced directly in the repository README.",
                "papers_count": 2872,
                "status": "Live Web Mirror"
            },
            {
                "name": "avallark/NCERT-TextBooks (GitHub Repository)",
                "category": "GitHub Open Source",
                "source_type": "git_repository",
                "url": "https://github.com/avallark/NCERT-TextBooks",
                "direct_repo_path": "/",
                "description": "Complete collection of standard NCERT textbooks from Class 1 to Class 12 in English & Hindi with chapter-wise and full-book PDFs.",
                "papers_count": 293,
                "status": "Active & Synchronized"
            },
            {
                "name": "suraj-deshmukh/pyq (GitHub Repository)",
                "category": "GitHub Open Source",
                "source_type": "git_repository",
                "url": "https://github.com/suraj-deshmukh/pyq",
                "direct_repo_path": "/",
                "description": "Educational indexing scripts and metadata schema for previous year exam papers.",
                "papers_count": 150,
                "status": "Active Reference"
            },

            # ── 2. SHABBER REPO DIRECT ACCESS FOLDERS ──
            {
                "name": "CBSE Board Examination Archive",
                "category": "CBSE Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/CBSE",
                "direct_repo_path": "Boards/CBSE",
                "description": "Class 10 and Class 12 CBSE Board examination papers from 2015 to 2023 across all subjects.",
                "papers_count": 895,
                "status": "Synchronized"
            },
            {
                "name": "ICSE & ISC Examination Archive",
                "category": "ICSE Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/ICSE",
                "direct_repo_path": "Boards/ICSE",
                "description": "Council for the Indian School Certificate Examinations (CISCE) question papers.",
                "papers_count": 5,
                "status": "Synchronized"
            },
            {
                "name": "Andhra Pradesh State Board Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Andhra_Pradesh",
                "direct_repo_path": "Boards/Andhra_Pradesh",
                "description": "BIEAP & BSEAP SSC and Intermediate Examination question papers.",
                "papers_count": 22,
                "status": "Synchronized"
            },
            {
                "name": "Bihar School Examination Board Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Bihar",
                "direct_repo_path": "Boards/Bihar",
                "description": "BSEB Matric (10th) and Intermediate (12th) question papers across subjects.",
                "papers_count": 32,
                "status": "Synchronized"
            },
            {
                "name": "Kerala State Board (DHSE / KBPE) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Kerala",
                "direct_repo_path": "Boards/Kerala",
                "description": "Kerala SSLC and Higher Secondary Plus Two examination question papers.",
                "papers_count": 7,
                "status": "Synchronized"
            },
            {
                "name": "Madhya Pradesh Board (MPBSE) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Madhya_Pradesh",
                "direct_repo_path": "Boards/Madhya_Pradesh",
                "description": "MP Board High School & Higher Secondary question papers.",
                "papers_count": 4,
                "status": "Synchronized"
            },
            {
                "name": "Maharashtra State Board (MSBSHSE) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Maharashtra",
                "direct_repo_path": "Boards/Maharashtra",
                "description": "Maharashtra SSC and HSC examination papers from 2014 to 2020.",
                "papers_count": 24,
                "status": "Synchronized"
            },
            {
                "name": "Rajasthan Board (RBSE) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Rajasthan",
                "direct_repo_path": "Boards/Rajasthan",
                "description": "RBSE Secondary and Senior Secondary exam papers.",
                "papers_count": 31,
                "status": "Synchronized"
            },
            {
                "name": "Tamil Nadu State Board (DGE) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Tamil_Nadu",
                "direct_repo_path": "Boards/Tamil_Nadu",
                "description": "Tamil Nadu SSLC 10th and HSC 12th Board question papers.",
                "papers_count": 12,
                "status": "Synchronized"
            },
            {
                "name": "Telangana State Board (TSBIE) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Telangana",
                "direct_repo_path": "Boards/Telangana",
                "description": "Telangana SSC and Intermediate papers.",
                "papers_count": 21,
                "status": "Synchronized"
            },
            {
                "name": "Uttar Pradesh Board (UPMSP) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/Uttar_Pradesh",
                "direct_repo_path": "Boards/Uttar_Pradesh",
                "description": "UP Board High School and Intermediate question papers.",
                "papers_count": 16,
                "status": "Synchronized"
            },
            {
                "name": "West Bengal Board (WBBSE / WBCHSE) Archive",
                "category": "State Boards",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/West_Bengal",
                "direct_repo_path": "Boards/West_Bengal",
                "description": "West Bengal Madhyamik and Higher Secondary question papers.",
                "papers_count": 6,
                "status": "Synchronized"
            },

            # ── 3. JEE & NEET ENTRANCE FOLDERS ──
            {
                "name": "JEE Main Examination Archive (2015–2026)",
                "category": "Engineering Entrance",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/JEE/Main",
                "direct_repo_path": "JEE/Main",
                "description": "NTA JEE Main shift-wise examination papers and official solution keys.",
                "papers_count": 176,
                "status": "Synchronized"
            },
            {
                "name": "JEE Advanced Examination Archive (2012–2024)",
                "category": "Engineering Entrance",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/JEE/Advanced",
                "direct_repo_path": "JEE/Advanced",
                "description": "IIT JEE Advanced Paper 1 and Paper 2 question papers and solution booklets.",
                "papers_count": 8,
                "status": "Synchronized"
            },
            {
                "name": "NEET UG Examination Archive (2016–2025)",
                "category": "Medical Entrance",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/NEET",
                "direct_repo_path": "NEET",
                "description": "National Eligibility cum Entrance Test (UG) question papers, phase papers, and code sets.",
                "papers_count": 98,
                "status": "Synchronized"
            },

            # ── 4. UPSC & DEFENCE FOLDERS ──
            {
                "name": "UPSC Civil Services Prelims Archive",
                "category": "Civil Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/Civil_Services/Prelims",
                "direct_repo_path": "UPSC/Civil_Services/Prelims",
                "description": "Civil Services Preliminary Examination GS Paper 1 and CSAT Paper 2 from 2016 to 2024.",
                "papers_count": 20,
                "status": "Synchronized"
            },
            {
                "name": "UPSC Civil Services Mains Archive",
                "category": "Civil Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/Civil_Services/Mains",
                "direct_repo_path": "UPSC/Civil_Services/Mains",
                "description": "Civil Services Main Examination Essay, GS 1 to 4, and optional subject papers.",
                "papers_count": 982,
                "status": "Synchronized"
            },
            {
                "name": "UPSC National Defence Academy (NDA) Archive",
                "category": "Defence Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/NDA",
                "direct_repo_path": "UPSC/NDA",
                "description": "NDA & NA Mathematics and General Ability Test (GAT) question papers across sessions.",
                "papers_count": 35,
                "status": "Synchronized"
            },
            {
                "name": "UPSC Combined Defence Services (CDS) Archive",
                "category": "Defence Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/CDS",
                "direct_repo_path": "UPSC/CDS",
                "description": "CDS English, General Knowledge, and Elementary Mathematics question papers.",
                "papers_count": 60,
                "status": "Synchronized"
            },
            {
                "name": "UPSC Central Armed Police Forces (CAPF) Archive",
                "category": "Defence Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/CAPF",
                "direct_repo_path": "UPSC/CAPF",
                "description": "CAPF Assistant Commandants Paper 1 (General Ability) and Paper 2 (Essay & Comprehension).",
                "papers_count": 15,
                "status": "Synchronized"
            },
            {
                "name": "UPSC Indian Forest Service (IFS) Archive",
                "category": "Civil Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/Indian_Forest_Service",
                "direct_repo_path": "UPSC/Indian_Forest_Service",
                "description": "Indian Forest Service Main examination papers in forestry, agriculture, botany, geology.",
                "papers_count": 264,
                "status": "Synchronized"
            },
            {
                "name": "UPSC Engineering Services Examination (ESE/IES) Archive",
                "category": "Technical Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/Engineering_Services",
                "direct_repo_path": "UPSC/Engineering_Services",
                "description": "Civil, Mechanical, Electrical, and Electronics & Telecom engineering papers.",
                "papers_count": 119,
                "status": "Synchronized"
            },
            {
                "name": "UPSC Combined Medical Services (CMS) Archive",
                "category": "Medical Services",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/UPSC/Combined_Medical_Services",
                "direct_repo_path": "UPSC/Combined_Medical_Services",
                "description": "Combined Medical Services Examination Paper 1 and Paper 2.",
                "papers_count": 20,
                "status": "Synchronized"
            },
            {
                "name": "PYQ & Quiz Diagram Image Archive",
                "category": "Visual Assets",
                "source_type": "github_folder",
                "url": "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Images",
                "direct_repo_path": "Images",
                "description": "36,800+ question diagram images, circuit diagrams, geometric figures, and chemistry structures extracted from PYQs.",
                "papers_count": 36800,
                "status": "Asset CDN"
            },

            # ── 5. STATUTORY BODIES & OFFICIAL PORTALS ──
            {
                "name": "Central Board of Secondary Education (CBSE Academic)",
                "category": "Official Portal",
                "source_type": "official_statutory",
                "url": "https://cbseacademic.nic.in",
                "direct_repo_path": "N/A",
                "description": "Statutory body governing Class 10 and 12 national examinations, sample papers, and marking schemes.",
                "papers_count": 1131,
                "status": "Statutory Authority"
            },
            {
                "name": "Union Public Service Commission (UPSC Official)",
                "category": "Official Portal",
                "source_type": "official_statutory",
                "url": "https://upsc.gov.in",
                "direct_repo_path": "N/A",
                "description": "Constitutional body conducting Civil Services, NDA, CDS, CAPF, IFS, ESE, and CMS examinations.",
                "papers_count": 1530,
                "status": "Constitutional Authority"
            },
            {
                "name": "National Testing Agency (NTA Official)",
                "category": "Official Portal",
                "source_type": "official_statutory",
                "url": "https://jeemain.nta.ac.in",
                "direct_repo_path": "N/A",
                "description": "Central autonomous testing organization conducting JEE Main, NEET UG, and national entrance tests.",
                "papers_count": 233,
                "status": "National Authority"
            },
            {
                "name": "Tamil Nadu Public Service Commission (TNPSC)",
                "category": "Official Portal",
                "source_type": "official_statutory",
                "url": "https://www.tnpsc.gov.in",
                "direct_repo_path": "N/A",
                "description": "State constitutional body administering Combined Civil Services Examinations in Tamil Nadu.",
                "papers_count": 61,
                "status": "State Authority"
            }
        ]

        for s in sources_data:
            cur.execute("""
                INSERT INTO sources (
                    name, category, source_type, url, direct_repo_path,
                    description, papers_count, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                s["name"], s["category"], s["source_type"], s["url"],
                s["direct_repo_path"], s["description"], s["papers_count"], s["status"]
            ))

        # ── CLASSIFY VERIFIED vs UNVERIFIED PAPERS ──
        print("Classifying Verified vs Unverified papers...")
        # 1. Unverified: upcoming / provisional years (2025, 2026), or papers explicitly lacking verified keys
        cur.execute("""
            UPDATE papers SET verification_status = 'unverified'
            WHERE year >= 2025
               OR title LIKE '%Shift 2%' AND year = 2026
               OR title LIKE '%NDA 2026%'
        """)
        unverified_cnt = cur.rowcount
        print(f"✓ Marked {unverified_cnt} provisional/upcoming papers as 'unverified'")

        # 2. Keep historical board and civil service papers as 'verified'
        cur.execute("SELECT COUNT(*) as v_cnt FROM papers WHERE verification_status = 'verified'")
        verified_cnt = cur.fetchone()["v_cnt"]

        cur.execute("SELECT COUNT(*) as u_cnt FROM papers WHERE verification_status = 'unverified'")
        unverified_total = cur.fetchone()["u_cnt"]

        print(f"Database Classification Status:")
        print(f"  🟢 Verified Papers:   {verified_cnt}")
        print(f"  🟡 Unverified Papers: {unverified_total}")
        print(f"  Total Papers:         {verified_cnt + unverified_total}")

    conn.commit()
    conn.close()
    print("✓ Successfully migrated and seeded all sources and verified/unverified classifications!")

if __name__ == "__main__":
    main()
