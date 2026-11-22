import os
import sys
import json
import pymysql.cursors

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "261008")
DB_NAME = os.getenv("MYSQL_DB", "examvault")

def migrate_and_seed_curriculum():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cur:
        # Create category_curriculum table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS category_curriculum (
                id INT AUTO_INCREMENT PRIMARY KEY,
                exam_slug VARCHAR(50) NOT NULL,
                category_slug VARCHAR(50) NOT NULL,
                subject_name VARCHAR(100) NOT NULL,
                academic_year VARCHAR(20) NOT NULL DEFAULT '2024-25',
                curriculum_title VARCHAR(255) NOT NULL,
                official_pdf_url VARCHAR(1000) NOT NULL,
                source_name VARCHAR(255) NOT NULL,
                source_url VARCHAR(1000),
                total_marks INT DEFAULT 100,
                exam_duration VARCHAR(50) DEFAULT '3 Hours',
                units_json JSON,
                curriculum_markdown LONGTEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_cat_subj (exam_slug, category_slug, subject_name),
                INDEX ix_cat (exam_slug, category_slug)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✓ Created or verified `category_curriculum` table")

        # Official curricula definitions
        curricula = [
            # 1. CBSE Class 10 — Mathematics
            {
                "exam_slug": "class-10",
                "category_slug": "cbse-10",
                "subject_name": "Mathematics",
                "curriculum_title": "CBSE Secondary School Curriculum — Mathematics (Standard & Basic) Code 041/241",
                "official_pdf_url": "https://cbseacademic.nic.in/web_material/CurriculumMain25/Sec/Maths_Sec_2024-25.pdf",
                "source_name": "CBSE Academic Official Portal (cbseacademic.nic.in)",
                "source_url": "https://cbseacademic.nic.in/curriculum_2025.html",
                "total_marks": 80,
                "exam_duration": "3 Hours",
                "units": [
                    {"unit_no": "I", "name": "Number Systems (Real Numbers)", "marks": 6, "topics": ["Fundamental Theorem of Arithmetic", "Irrational Numbers Proofs", "Decimal Expansions"]},
                    {"unit_no": "II", "name": "Algebra", "marks": 20, "topics": ["Polynomials & Zeroes", "Pair of Linear Equations in Two Variables", "Quadratic Equations", "Arithmetic Progressions"]},
                    {"unit_no": "III", "name": "Coordinate Geometry", "marks": 6, "topics": ["Distance Formula", "Section Formula", "Collinearity"]},
                    {"unit_no": "IV", "name": "Geometry (Triangles & Circles)", "marks": 15, "topics": ["Basic Proportionality Theorem", "Similarity Criteria", "Tangents to Circles"]},
                    {"unit_no": "V", "name": "Trigonometry", "marks": 12, "topics": ["Trigonometric Ratios & Angles", "Trigonometric Identities (sin²θ+cos²θ=1)", "Heights and Distances"]},
                    {"unit_no": "VI", "name": "Mensuration (Areas & Volumes)", "marks": 10, "topics": ["Areas of Sectors and Segments", "Surface Areas and Volumes of Combinations of Solids"]},
                    {"unit_no": "VII", "name": "Statistics & Probability", "marks": 11, "topics": ["Mean, Median, Mode of Grouped Data", "Classical Definition of Probability"]}
                ],
                "markdown": "## CBSE Class 10 Mathematics Syllabus (2024-25)\nTheory: 80 Marks | Internal Assessment: 20 Marks | Total: 100 Marks\n- Internal Assessment: Pen-paper tests & multiple assessments (10 marks), Portfolio (5 marks), Lab practicals (5 marks)."
            },
            # 2. CBSE Class 10 — Science
            {
                "exam_slug": "class-10",
                "category_slug": "cbse-10",
                "subject_name": "Science",
                "curriculum_title": "CBSE Secondary School Curriculum — Science (Code 086)",
                "official_pdf_url": "https://cbseacademic.nic.in/web_material/CurriculumMain25/Sec/Science_Sec_2024-25.pdf",
                "source_name": "CBSE Academic Official Portal (cbseacademic.nic.in)",
                "source_url": "https://cbseacademic.nic.in/curriculum_2025.html",
                "total_marks": 80,
                "exam_duration": "3 Hours",
                "units": [
                    {"unit_no": "I", "name": "Chemical Substances - Nature & Behaviour", "marks": 25, "topics": ["Chemical Reactions & Balancing", "Acids, Bases & Salts", "Metals and Non-metals", "Carbon and its Compounds"]},
                    {"unit_no": "II", "name": "World of Living (Biology)", "marks": 25, "topics": ["Life Processes (Nutrition, Respiration, Circulation, Excretion)", "Control and Coordination", "Reproduction in Plants & Animals", "Heredity and Evolution"]},
                    {"unit_no": "III", "name": "Natural Phenomena (Light)", "marks": 12, "topics": ["Reflection by Spherical Mirrors", "Refraction & Snell's Law", "Lenses and Lens Formula", "Human Eye & Dispersion of Light"]},
                    {"unit_no": "IV", "name": "Effects of Current (Electricity & Magnetism)", "marks": 13, "topics": ["Ohm's Law, Resistance in Series/Parallel", "Joule's Law of Heating", "Magnetic Field & Fleming's Left-Hand Rule", "Electromagnetic Induction"]},
                    {"unit_no": "V", "name": "Natural Resources (Environment)", "marks": 5, "topics": ["Ecosystems & Food Chains", "Ozone Layer Depletion", "Waste Management"]}
                ],
                "markdown": "## CBSE Class 10 Science Syllabus (2024-25)\nComprehensive physics, chemistry, and biology integrated curriculum."
            },
            # 3. CBSE Class 12 — Physics
            {
                "exam_slug": "class-12",
                "category_slug": "cbse-12",
                "subject_name": "Physics",
                "curriculum_title": "CBSE Senior School Curriculum — Physics (Code 042)",
                "official_pdf_url": "https://cbseacademic.nic.in/web_material/CurriculumMain25/SrSec/Physics_SrSec_2024-25.pdf",
                "source_name": "CBSE Academic Official Portal (cbseacademic.nic.in)",
                "source_url": "https://cbseacademic.nic.in/curriculum_2025.html",
                "total_marks": 70,
                "exam_duration": "3 Hours",
                "units": [
                    {"unit_no": "I & II", "name": "Electrostatics & Current Electricity", "marks": 16, "topics": ["Coulomb's Law & Gauss's Theorem", "Electric Potential & Capacitance", "Drift Velocity & Ohm's Law", "Kirchhoff's Rules & Potentiometer"]},
                    {"unit_no": "III & IV", "name": "Magnetic Effects of Current & EMI/AC", "marks": 17, "topics": ["Biot-Savart Law & Ampere's Law", "Faraday's & Lenz's Laws", "LCR Series Circuit & Resonance", "Transformers & AC Generators"]},
                    {"unit_no": "V & VI", "name": "Electromagnetic Waves & Optics", "marks": 18, "topics": ["Displacement Current", "Ray Optics & Optical Instruments", "Wave Optics: Huygens Principle & Interference", "Diffraction by Single Slit"]},
                    {"unit_no": "VII & VIII", "name": "Dual Nature, Atoms & Nuclei", "marks": 12, "topics": ["Photoelectric Effect & Einstein's Equation", "Bohr Model of Hydrogen Atom", "Nuclear Binding Energy & Fission/Fusion"]},
                    {"unit_no": "IX", "name": "Electronic Devices (Semiconductors)", "marks": 7, "topics": ["p-n Junction Diode (Forward/Reverse Bias)", "Diode as a Rectifier (Half/Full Wave)"]}
                ],
                "markdown": "## CBSE Class 12 Physics Syllabus (2024-25)\nTheory: 70 Marks | Practical: 30 Marks."
            },
            # 4. CBSE Class 12 — Chemistry
            {
                "exam_slug": "class-12",
                "category_slug": "cbse-12",
                "subject_name": "Chemistry",
                "curriculum_title": "CBSE Senior School Curriculum — Chemistry (Code 043)",
                "official_pdf_url": "https://cbseacademic.nic.in/web_material/CurriculumMain25/SrSec/Chemistry_SrSec_2024-25.pdf",
                "source_name": "CBSE Academic Official Portal (cbseacademic.nic.in)",
                "source_url": "https://cbseacademic.nic.in/curriculum_2025.html",
                "total_marks": 70,
                "exam_duration": "3 Hours",
                "units": [
                    {"unit_no": "I-III", "name": "Physical Chemistry (Solutions, Electrochemistry, Kinetics)", "marks": 23, "topics": ["Raoult's Law & Colligative Properties", "Nernst Equation & Kohlrausch's Law", "Rate Laws, Arrhenius Equation & Half Life"]},
                    {"unit_no": "IV-V", "name": "Inorganic Chemistry (d/f-Block & Coordination)", "marks": 14, "topics": ["Electronic Configuration of d & f Block", "Crystal Field Theory & Isomerism", "Nomenclature of Coordination Compounds"]},
                    {"unit_no": "VI-X", "name": "Organic Chemistry", "marks": 33, "topics": ["Haloalkanes & Haloarenes (SN1/SN2)", "Alcohols, Phenols and Ethers", "Aldehydes, Ketones & Carboxylic Acids", "Amines & Diazonium Salts", "Biomolecules (Proteins, DNA/RNA)"]}
                ],
                "markdown": "## CBSE Class 12 Chemistry Syllabus (2024-25)\nPhysical (23 Marks), Inorganic (14 Marks), Organic (33 Marks)."
            },
            # 5. UPSC Prelims — General Studies & CSAT
            {
                "exam_slug": "upsc",
                "category_slug": "prelims",
                "subject_name": "General Studies",
                "curriculum_title": "UPSC Civil Services Examination Gazette — Prelims Stage Syllabus",
                "official_pdf_url": "https://upsc.gov.in/sites/default/files/Notif-CSP-2024-engl-140224.pdf",
                "source_name": "Union Public Service Commission (upsc.gov.in)",
                "source_url": "https://upsc.gov.in/examinations/civil-services-preliminary-examination-2024",
                "total_marks": 400,
                "exam_duration": "4 Hours (2 Sessions of 2h each)",
                "units": [
                    {"unit_no": "Paper I", "name": "General Studies Paper I (Merit Ranking)", "marks": 200, "topics": ["Current events of National and International Importance", "History of India and Indian National Movement", "Indian and World Geography (Physical, Social, Economic)", "Indian Polity and Governance (Constitution, Panchayati Raj, Public Policy)", "Economic and Social Development (Poverty, Inclusion, Demographics)", "General issues on Environmental Ecology, Bio-diversity and Climate Change", "General Science & Tech"]},
                    {"unit_no": "Paper II", "name": "Civil Services Aptitude Test / CSAT (Qualifying 33%)", "marks": 200, "topics": ["Comprehension & Interpersonal Skills", "Logical Reasoning and Analytical Ability", "Decision Making and Problem Solving", "General Mental Ability", "Basic Numeracy (Class X level)", "Data Interpretation (charts, graphs, tables)"]}
                ],
                "markdown": "## UPSC Civil Services Examination Prelims Syllabus\nPaper I (200 marks, counts for Mains qualification) + Paper II (CSAT, 33% qualifying)."
            },
            # 6. UPSC Mains — GS & Essay
            {
                "exam_slug": "upsc",
                "category_slug": "mains",
                "subject_name": "General Studies",
                "curriculum_title": "UPSC Civil Services Examination Gazette — Mains Written Examination",
                "official_pdf_url": "https://upsc.gov.in/sites/default/files/Notif-CSP-2024-engl-140224.pdf",
                "source_name": "Union Public Service Commission (upsc.gov.in)",
                "source_url": "https://upsc.gov.in/examinations/civil-services-main-examination-2024",
                "total_marks": 1750,
                "exam_duration": "9 Papers of 3 Hours each",
                "units": [
                    {"unit_no": "Paper I", "name": "Essay (Two Sections: Philosophical & Concrete)", "marks": 250, "topics": ["Multi-dimensional socio-economic and ethical essays"]},
                    {"unit_no": "Paper II", "name": "General Studies I (Heritage, History, Society & Geography)", "marks": 250, "topics": ["Indian Art and Culture", "Modern Indian History (1757-1947)", "World History (Industrial Rev to Cold War)", "Indian Society & Diversity", "Physical & Human Geography"]},
                    {"unit_no": "Paper III", "name": "General Studies II (Governance, Constitution, Polity & IR)", "marks": 250, "topics": ["Indian Constitution & Federalism", "Parliament & State Legislatures", "Welfare Schemes & Governance", "Bilateral & Regional International Relations"]},
                    {"unit_no": "Paper IV", "name": "General Studies III (Economy, Sci-Tech, Ecology & Security)", "marks": 250, "topics": ["Indian Economy, Budgeting & Inclusive Growth", "Agriculture & Food Processing", "Science & Technology Innovations", "Disaster Management & Security Challenges"]},
                    {"unit_no": "Paper V", "name": "General Studies IV (Ethics, Integrity and Aptitude)", "marks": 250, "topics": ["Ethics in Public Administration", "Emotional Intelligence", "Moral Thinkers & Philosophers", "Real-world Case Studies on Integrity"]},
                    {"unit_no": "Papers VI-VII", "name": "Optional Subject (Paper I & II)", "marks": 500, "topics": ["In-depth specialized subject of candidate's choice"]}
                ],
                "markdown": "## UPSC Civil Services Mains Examination Structure\nTotal 1750 marks written + 275 marks Personality Test = 2025 Grand Total."
            },
            # 7. JEE Advanced
            {
                "exam_slug": "jee",
                "category_slug": "jee-advanced",
                "subject_name": "Physics",
                "curriculum_title": "JEE (Advanced) Official Information Bulletin & Syllabus",
                "official_pdf_url": "https://jeeadv.ac.in/documents/jee-advanced-2024-syllabus.pdf",
                "source_name": "IIT Madras / JEE (Advanced) Office",
                "source_url": "https://jeeadv.ac.in",
                "total_marks": 360,
                "exam_duration": "Two Papers of 3 Hours each",
                "units": [
                    {"unit_no": "Unit I", "name": "Physics (Mechanics, Thermal, Wave, Electrodynamics, Optics)", "marks": 120, "topics": ["Kinematics & Newton's Laws", "Rotational Dynamics & Moment of Inertia", "Fluid Mechanics & Surface Tension", "Thermodynamics & Heat Engines", "Electromagnetism & Maxwell Equations", "Wave Optics & Modern Physics"]},
                    {"unit_no": "Unit II", "name": "Chemistry (Physical, Inorganic & Organic Chemistry)", "marks": 120, "topics": ["Atomic Structure & Chemical Bonding", "Chemical Equilibrium & Kinetics", "Coordination Compounds & Metallurgy", "Reaction Mechanisms (Electrophilic/Nucleophilic)", "Aromatic Compounds & Polymers"]},
                    {"unit_no": "Unit III", "name": "Mathematics (Algebra, Calculus, Coordinate Geometry, Vectors)", "marks": 120, "topics": ["Complex Numbers & Quadratic Equations", "Differential & Integral Calculus", "Differential Equations", "Conic Sections (Parabola, Ellipse, Hyperbola)", "3D Geometry and Vector Algebra", "Probability & Binomial Theorem"]}
                ],
                "markdown": "## JEE (Advanced) Examination Curriculum\nRigorous conceptual multi-correct, integer, and comprehension question formats."
            },
            # 8. NEET UG
            {
                "exam_slug": "neet",
                "category_slug": "neet-ug",
                "subject_name": "Biology",
                "curriculum_title": "National Medical Commission (NMC) NEET (UG) Syllabus",
                "official_pdf_url": "https://www.nmc.org.in/MCIRest/open/getDocument?path=/Documents/Public/Portal/LatestNews/NEET_UG_2024_Syllabus.pdf",
                "source_name": "National Testing Agency (neet.nta.nic.in) / NMC",
                "source_url": "https://neet.nta.nic.in",
                "total_marks": 720,
                "exam_duration": "3 Hours 20 Minutes (200 Qs, attempt 180)",
                "units": [
                    {"unit_no": "Physics", "name": "Physics (Class XI & XII Core)", "marks": 180, "topics": ["Kinematics & Laws of Motion", "Work, Energy & Power", "Thermodynamics & Properties of Bulk Matter", "Oscillations & Waves", "Electrostatics & Current Electricity", "Magnetic Effects of Current & Magnetism", "Optics & Modern Physics"]},
                    {"unit_no": "Chemistry", "name": "Chemistry (Physical, Inorganic, Organic)", "marks": 180, "topics": ["Structure of Atom & Periodic Classification", "Chemical Bonding & Molecular Structure", "Thermodynamics & Equilibrium", "Redox & Electrochemistry", "p-Block, d-Block & Coordination Compounds", "Hydrocarbons, Aldehydes, Ketones, Carboxylic Acids & Amines"]},
                    {"unit_no": "Biology", "name": "Biology (Botany & Zoology)", "marks": 360, "topics": ["Diversity in Living World & Taxonomy", "Structural Organisation in Animals and Plants", "Cell Structure and Function (Biomolecules, Mitosis/Meiosis)", "Plant Physiology (Photosynthesis, Respiration)", "Human Physiology (Digestion, Circulation, Nervous System)", "Genetics and Molecular Basis of Inheritance", "Biotechnology Principles & Applications", "Ecology and Environment"]}
                ],
                "markdown": "## NEET UG Examination Curriculum\nTotal 720 Marks. Marking: +4 for correct, -1 for incorrect."
            },
            # 9. TNPSC Group 1
            {
                "exam_slug": "tnpsc",
                "category_slug": "group-1",
                "subject_name": "General Studies",
                "curriculum_title": "TNPSC Group 1 Combined Civil Services Preliminary Examination Scheme",
                "official_pdf_url": "https://www.tnpsc.gov.in/static_pdf/syllabus/G1-Prelims-Syllabus.pdf",
                "source_name": "Tamil Nadu Public Service Commission (tnpsc.gov.in)",
                "source_url": "https://www.tnpsc.gov.in",
                "total_marks": 300,
                "exam_duration": "3 Hours (200 Questions)",
                "units": [
                    {"unit_no": "Unit I", "name": "General Science (Physics, Chemistry, Botany, Zoology)", "marks": 25, "topics": ["Scientific Knowledge & Scientific Temper", "Nature of Universe, General Scientific Laws", "Mechanics and Properties of Matter", "Elements and Compounds, Acids/Bases", "Life Science, Physiology & Nutrition"]},
                    {"unit_no": "Unit II", "name": "Current Events (History, Political Science, Geography, Economics)", "marks": 25, "topics": ["Latest diary of events - National & State symbols", "Awards and Honours, India and its neighbours", "Sports, Books & Authors", "Science & Technology updates"]},
                    {"unit_no": "Unit III", "name": "Geography of India and Tamil Nadu", "marks": 25, "topics": ["Location, Physical features, Monsoon, Rainfall", "Water resources, Rivers in India and TN", "Soil, Minerals & Natural resources", "Forest & wildlife, Agricultural pattern"]},
                    {"unit_no": "Unit IV", "name": "History and Culture of India", "marks": 25, "topics": ["Indus valley civilization, Guptas, Delhi Sultans, Mughals and Marathas", "Age of Vijayanagaram and Bahmani Kingdoms", "South Indian history, Culture & Heritage"]},
                    {"unit_no": "Unit V", "name": "Indian Polity", "marks": 25, "topics": ["Constitution of India - Preamble to Constitution", "Salient features, Union, State and Union territory", "Fundamental Rights, Fundamental duties", "Directive Principles of State policy", "Panchayat Raj & Anti-corruption measures"]},
                    {"unit_no": "Unit VI", "name": "Indian Economy", "marks": 25, "topics": ["Nature of Indian economy - Five year plan models", "Planning Commission and Niti Aayog", "Sources of revenue - Reserve Bank of India", "Fiscal Policy and Monetary Policy, Goods and Services Tax (GST)"]},
                    {"unit_no": "Unit VII", "name": "Indian National Movement", "marks": 25, "topics": ["National renaissance - Early uprising against British rule", "Indian National Congress, Emergence of leaders", "Different modes of agitations, Communalism and partition"]},
                    {"unit_no": "Unit VIII", "name": "History, Culture, Heritage and Socio-Political Movements in TN", "marks": 40, "topics": ["History of Tamil Society, Archaeological discoveries, Tamil Literature from Sangam age", "Thirukkural philosophy and governance relevance", "Role of Tamil Nadu in freedom struggle, Self-Respect Movement, Dravidian Movement"]},
                    {"unit_no": "Unit IX", "name": "Development Administration in Tamil Nadu", "marks": 35, "topics": ["Human Development Indicators in TN, Social welfare schemes", "Economic trends in TN, E-governance in TN"]},
                    {"unit_no": "Unit X", "name": "Aptitude and Mental Ability", "marks": 50, "topics": ["Simplification, Percentage, HCF & LCM, Ratio and Proportion", "Simple interest & Compound interest, Area, Volume, Time and Work", "Logical Reasoning, Puzzles, Dice, Visual Reasoning"]}
                ],
                "markdown": "## TNPSC Group 1 Examination Syllabus (Units 1 to 10)\nComprehensive state and national administrative syllabus."
            }
        ]

        for item in curricula:
            cur.execute("""
                INSERT INTO category_curriculum (
                    exam_slug, category_slug, subject_name, academic_year,
                    curriculum_title, official_pdf_url, source_name, source_url,
                    total_marks, exam_duration, units_json, curriculum_markdown
                ) VALUES (
                    %s, %s, %s, '2024-25',
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                ) ON DUPLICATE KEY UPDATE
                    curriculum_title = VALUES(curriculum_title),
                    official_pdf_url = VALUES(official_pdf_url),
                    source_name = VALUES(source_name),
                    source_url = VALUES(source_url),
                    total_marks = VALUES(total_marks),
                    exam_duration = VALUES(exam_duration),
                    units_json = VALUES(units_json),
                    curriculum_markdown = VALUES(curriculum_markdown)
            """, (
                item["exam_slug"], item["category_slug"], item["subject_name"],
                item["curriculum_title"], item["official_pdf_url"], item["source_name"], item["source_url"],
                item["total_marks"], item["exam_duration"], json.dumps(item["units"]), item["markdown"]
            ))

    conn.commit()
    conn.close()
    print("✓ Successfully migrated and seeded official statutory curricula into `category_curriculum`!")

if __name__ == "__main__":
    migrate_and_seed_curriculum()
