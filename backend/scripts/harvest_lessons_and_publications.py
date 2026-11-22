"""
Harvest & Seed Complete Subject-to-Lesson / Chapter Architecture with
Curated Questions from Oswaal Books, NCERT Exemplar, Arihant/MTG, and Board PYQs.
Co-locates textbook chapters with targeted lesson questions across:
- Class 10 (Science, Maths, Social Science)
- Class 12 (Physics, Chemistry, Maths, Biology)
- JEE Main & Advanced
- NEET UG
- UPSC Civil Services
- TNPSC
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.db import get_db

app = create_app()

CHAPTERS_DATA = [
    # ── CLASS 10 SCIENCE (Subject: Science - ID 28) ──────────────────────────
    {
        "exam_slug": "class-10", "std": "Class 10", "subj_name": "Science",
        "board": "CBSE / NCERT / Oswaal", "num": 1, "title": "Chemical Reactions and Equations",
        "weightage": "4-6 Marks",
        "summary": "Covers combination, decomposition, displacement, double displacement, precipitation, and redox reactions. Key concepts: Law of conservation of mass, oxidation states, and balancing equations.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Science/jesc101.pdf",
        "questions": [
            {
                "text": "Why should a magnesium ribbon be cleaned before burning in air? Give the balanced chemical equation for the reaction.",
                "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2024,
                "src": "Oswaal CBSE Class 10 Science Question Bank",
                "ans": "Magnesium is a reactive metal. When stored, it reacts with atmospheric oxygen to form a thin, protective layer of basic magnesium oxide (MgO) on its surface, which hinders burning. Cleaning with sandpaper exposes the fresh metal. Equation: 2Mg(s) + O2(g) -> 2MgO(s)."
            },
            {
                "text": "Identify the substance oxidized, substance reduced, oxidizing agent, and reducing agent in: MnO2 + 4HCl -> MnCl2 + 2H2O + Cl2.",
                "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2023,
                "src": "NCERT Exemplar Class 10 Problems",
                "ans": "Substance oxidized: HCl (loses hydrogen to form Cl2). Substance reduced: MnO2 (loses oxygen to form MnCl2). Oxidizing agent: MnO2. Reducing agent: HCl."
            },
            {
                "text": "A shiny brown colored element 'X' on heating in air becomes black in color. Name the element 'X' and the black colored compound formed. Write the balanced equation.",
                "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2022,
                "src": "CBSE Official Board Question Paper",
                "ans": "Element 'X' is Copper (Cu). The black colored compound formed is Copper(II) Oxide (CuO). Equation: 2Cu(s) + O2(g) --[Heat]--> 2CuO(s)."
            }
        ]
    },
    {
        "exam_slug": "class-10", "std": "Class 10", "subj_name": "Science",
        "board": "CBSE / NCERT / Oswaal", "num": 2, "title": "Acids, Bases and Salts",
        "weightage": "5-7 Marks",
        "summary": "Chemical properties of acids and bases, pH scale in everyday life, preparation and uses of Bleaching Powder, Baking Soda, Washing Soda, and Plaster of Paris.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Science/jesc102.pdf",
        "questions": [
            {
                "text": "Why does dry HCl gas not change the colour of the dry litmus paper?",
                "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2024,
                "src": "Oswaal CBSE Class 10 Science Question Bank",
                "ans": "Dry HCl gas does not ionize in the absence of water to produce hydrogen ions (H+ or H3O+). Since acidic behavior is due to H+ ions, dry litmus paper does not change color."
            },
            {
                "text": "Write the chemical formula and preparation equation of Plaster of Paris. Why should it be stored in a moisture-proof container?",
                "type": "Long Answer", "marks": 3, "diff": "Medium", "year": 2023,
                "src": "NCERT Exemplar Class 10 Problems",
                "ans": "Chemical formula: CaSO4 . 1/2 H2O (Calcium Sulphate Hemihydrate). Prepared by heating Gypsum (CaSO4 . 2H2O) at 373 K: CaSO4.2H2O -> CaSO4.1/2H2O + 1.5H2O. Must be stored in moisture-proof containers because it absorbs water to set into hard solid Gypsum again."
            }
        ]
    },
    {
        "exam_slug": "class-10", "std": "Class 10", "subj_name": "Science",
        "board": "CBSE / NCERT / Oswaal", "num": 9, "title": "Light - Reflection and Refraction",
        "weightage": "7-9 Marks",
        "summary": "Laws of reflection, spherical mirrors (concave/convex), mirror formula, magnification, laws of refraction, Snell's law, refractive index, lens formula, and power of a lens.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Science/jesc109.pdf",
        "questions": [
            {
                "text": "A convex lens forms a real and inverted image of a needle at a distance of 50 cm from it. Where is the needle placed in front of the convex lens if the image is equal to the size of the object? Also find the power of the lens.",
                "type": "Numerical", "marks": 3, "diff": "Medium", "year": 2024,
                "src": "Oswaal CBSE Chapterwise Question Bank",
                "ans": "When image is real, inverted and same size, object is at 2F1: v = +50 cm, so u = -50 cm. Focal length f = v/2 = 25 cm = +0.25 m. Power P = 1/f(m) = 1/0.25 = +4.0 Dioptres (+4D)."
            },
            {
                "text": "State Snell's law of refraction. Write the expression for absolute refractive index in terms of speed of light.",
                "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2023,
                "src": "CBSE Official Board Question Paper",
                "ans": "Snell's Law: The ratio of sine of angle of incidence to sine of angle of refraction is constant for light of a given color and for a given pair of media: sin(i) / sin(r) = constant = n21. Absolute refractive index n = c / v (speed of light in vacuum / speed in medium)."
            }
        ]
    },
    {
        "exam_slug": "class-10", "std": "Class 10", "subj_name": "Science",
        "board": "CBSE / NCERT / Oswaal", "num": 11, "title": "Electricity",
        "weightage": "6-8 Marks",
        "summary": "Electric current, potential difference, Ohm's law, resistance, resistivity, factors affecting resistance, series and parallel resistor circuits, Joule's heating law, and electric power.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Science/jesc111.pdf",
        "questions": [
            {
                "text": "State Ohm's Law. Draw a circuit diagram to verify it. What is the shape of V-I graph for an ohmic conductor?",
                "type": "Long Answer", "marks": 4, "diff": "Medium", "year": 2024,
                "src": "Oswaal CBSE Class 10 Science Question Bank",
                "ans": "Ohm's Law: The electric current flowing through a metallic conductor is directly proportional to the potential difference across its terminals, provided temperature remains constant: V = I * R. The V-I graph is a straight line passing through the origin."
            },
            {
                "text": "A wire of resistance R is cut into five equal parts. These parts are then connected in parallel. If the equivalent resistance of this combination is R', then find the ratio R/R'.",
                "type": "MCQ", "marks": 1, "diff": "Medium", "year": 2023,
                "src": "NCERT Exemplar Class 10 Problems",
                "ans": "Resistance of each piece is R/5. When 5 such pieces are connected in parallel: 1/R' = 5/(R/5) = 25/R. Therefore R' = R/25, which gives the ratio R / R' = 25."
            }
        ]
    },

    # ── CLASS 10 MATHEMATICS (Subject: Mathematics - ID 48) ──────────────────
    {
        "exam_slug": "class-10", "std": "Class 10", "subj_name": "Mathematics",
        "board": "CBSE / NCERT / Oswaal", "num": 1, "title": "Real Numbers",
        "weightage": "6 Marks",
        "summary": "Fundamental Theorem of Arithmetic, proving irrationality of sqrt(2), sqrt(3), sqrt(5), prime factorisation method for HCF and LCM.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Mathematics/jemh101.pdf",
        "questions": [
            {
                "text": "Prove that sqrt(5) is an irrational number.",
                "type": "Proof", "marks": 3, "diff": "Medium", "year": 2024,
                "src": "Oswaal CBSE 10th Mathematics Question Bank",
                "ans": "Assume to contrary sqrt(5) = a/b where a, b are coprime integers (b != 0). Squaring gives 5 = a^2 / b^2 => 5b^2 = a^2. Thus 5 divides a^2, which implies 5 divides a. Let a = 5k. Then 5b^2 = 25k^2 => b^2 = 5k^2, so 5 divides b. This contradicts that a, b are coprime. Hence sqrt(5) is irrational."
            },
            {
                "text": "If HCF(306, 657) = 9, find LCM(306, 657).",
                "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2023,
                "src": "NCERT Mathematics Exemplar",
                "ans": "Product of two numbers = HCF * LCM. 306 * 657 = 9 * LCM => LCM = (306 * 657) / 9 = 34 * 657 = 22,338."
            }
        ]
    },
    {
        "exam_slug": "class-10", "std": "Class 10", "subj_name": "Mathematics",
        "board": "CBSE / NCERT / Oswaal", "num": 4, "title": "Quadratic Equations",
        "weightage": "6-8 Marks",
        "summary": "Standard form ax^2 + bx + c = 0, solution by factorisation and quadratic formula, nature of roots based on discriminant D = b^2 - 4ac.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Mathematics/jemh104.pdf",
        "questions": [
            {
                "text": "Find the values of k for which the quadratic equation (k + 1)x^2 - 2(k - 1)x + 1 = 0 has real and equal roots.",
                "type": "Short Answer", "marks": 3, "diff": "Medium", "year": 2024,
                "src": "Oswaal CBSE 10th Mathematics Question Bank",
                "ans": "For real and equal roots, Discriminant D = 0. D = [-2(k - 1)]^2 - 4(k + 1)(1) = 4(k^2 - 2k + 1) - 4k - 4 = 4k^2 - 12k = 4k(k - 3) = 0. Since k + 1 != 0 (k != -1), k = 0 or k = 3."
            }
        ]
    },
    {
        "exam_slug": "class-10", "std": "Class 10", "subj_name": "Mathematics",
        "board": "CBSE / NCERT / Oswaal", "num": 8, "title": "Introduction to Trigonometry",
        "weightage": "8-10 Marks",
        "summary": "Trigonometric ratios of acute angles, values at 0, 30, 45, 60, 90 degrees, trigonometric identities: sin^2 + cos^2 = 1, 1 + tan^2 = sec^2, 1 + cot^2 = cosec^2.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Mathematics/jemh108.pdf",
        "questions": [
            {
                "text": "Prove that: (sin theta - 2 sin^3 theta) / (2 cos^3 theta - cos theta) = tan theta.",
                "type": "Proof", "marks": 4, "diff": "Hard", "year": 2024,
                "src": "CBSE Official Board Question Paper",
                "ans": "LHS = [sin theta (1 - 2 sin^2 theta)] / [cos theta (2 cos^2 theta - 1)]. Substitute 1 = sin^2 theta + cos^2 theta in numerator: 1 - 2 sin^2 theta = cos^2 theta - sin^2 theta. In denominator: 2 cos^2 theta - 1 = cos^2 theta - sin^2 theta. The terms cancel: sin theta / cos theta = tan theta = RHS."
            }
        ]
    },

    # ── CLASS 12 PHYSICS (Subject: Physics - ID 46) ──────────────────────────
    {
        "exam_slug": "class-12", "std": "Class 12", "subj_name": "Physics",
        "board": "CBSE / NCERT / Oswaal", "num": 1, "title": "Electric Charges and Fields",
        "weightage": "8-9 Marks",
        "summary": "Coulomb's Law, forces between multiple charges, electric field, electric field lines, electric dipole, torque on dipole, Gauss's law and its applications.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2012/Physics/leph101.pdf",
        "questions": [
            {
                "text": "State Gauss's Law in electrostatics. Using it, derive the expression for electric field due to an infinitely long straight uniformly charged wire.",
                "type": "Derivation", "marks": 5, "diff": "Medium", "year": 2024,
                "src": "Oswaal CBSE Class 12 Physics Question Bank",
                "ans": "Gauss's Law states that total electric flux through any closed surface is 1/epsilon0 times the net charge enclosed: oint E . dA = q_enclosed / epsilon0. Considering a cylindrical Gaussian surface of radius r and length l coaxial with the wire of linear charge density lambda: E * (2 * pi * r * l) = (lambda * l) / epsilon0 => E = lambda / (2 * pi * epsilon0 * r)."
            },
            {
                "text": "Derive the expression for torque acting on an electric dipole of dipole moment p placed in a uniform electric field E.",
                "type": "Derivation", "marks": 3, "diff": "Medium", "year": 2023,
                "src": "NCERT Exemplar Class 12 Physics",
                "ans": "Forces on +q and -q are +qE and -qE (net force is zero). The perpendicular distance between line of action of forces is 2a * sin(theta). Torque tau = Force * perp. distance = qE * 2a * sin(theta) = (q * 2a) * E * sin(theta) = p * E * sin(theta) => tau = p x E."
            }
        ]
    },
    {
        "exam_slug": "class-12", "std": "Class 12", "subj_name": "Physics",
        "board": "CBSE / NCERT / Oswaal", "num": 3, "title": "Current Electricity",
        "weightage": "7 Marks",
        "summary": "Electric current, drift velocity, mobility, Ohm's law, temperature dependence of resistance, Kirchhoff's laws, Wheatstone bridge.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2012/Physics/leph103.pdf",
        "questions": [
            {
                "text": "Derive the relation between drift velocity (v_d) of free electrons and electric current (I) in a conductor.",
                "type": "Derivation", "marks": 3, "diff": "Medium", "year": 2024,
                "src": "Oswaal CBSE Class 12 Physics Question Bank",
                "ans": "Let n be free electron density, A be cross-sectional area, v_d be drift velocity. In time dt, distance traversed is v_d * dt. Volume = A * v_d * dt. Number of electrons = n * A * v_d * dt. Total charge dq = n * A * v_d * e * dt. Current I = dq / dt = n * e * A * v_d."
            }
        ]
    },

    # ── CLASS 12 CHEMISTRY (Subject: Chemistry - ID 47) ──────────────────────
    {
        "exam_slug": "class-12", "std": "Class 12", "subj_name": "Chemistry",
        "board": "CBSE / NCERT / Oswaal", "num": 1, "title": "Solutions",
        "weightage": "7 Marks",
        "summary": "Types of solutions, Raoult's law, colligative properties (elevation in boiling point, depression in freezing point, osmotic pressure), van't Hoff factor.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2012/Chemistry/lech101.pdf",
        "questions": [
            {
                "text": "State Henry's Law and mention two of its important applications in biological and industrial processes.",
                "type": "Short Answer", "marks": 2, "diff": "Easy", "year": 2024,
                "src": "Oswaal CBSE Class 12 Chemistry Question Bank",
                "ans": "Henry's Law states that at constant temperature, solubility of a gas in a liquid is directly proportional to partial pressure of the gas: p = K_H * x. Applications: (1) In soft drinks and soda water bottles sealed under high pressure to increase CO2 solubility. (2) Deep-sea divers use helium-diluted oxygen to prevent nitrogen narcosis and the bends."
            },
            {
                "text": "Calculate the freezing point depression of a 0.1 molal aqueous solution of CaCl2 assuming complete dissociation (Kf for water = 1.86 K kg/mol).",
                "type": "Numerical", "marks": 3, "diff": "Medium", "year": 2023,
                "src": "NCERT Exemplar Class 12 Chemistry",
                "ans": "CaCl2 dissociates into Ca2+ + 2Cl-, so van't Hoff factor i = 3. Delta Tf = i * Kf * m = 3 * 1.86 * 0.1 = 0.558 K. The freezing point of the solution is 273.15 - 0.558 = 272.592 K (-0.558 deg C)."
            }
        ]
    },

    # ── JEE MAIN & ADVANCED (Subject: Physics - ID 46, Maths - ID 48) ────────
    {
        "exam_slug": "jee", "std": "JEE", "subj_name": "Physics",
        "board": "NTA / JEE Advanced / Arihant", "num": 1, "title": "Rotational Motion and Rigid Body Dynamics",
        "weightage": "8-12 Marks",
        "summary": "Centre of mass, moment of inertia, parallel and perpendicular axis theorems, torque, angular momentum conservation, rolling without slipping.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2011/Physics/keph107.pdf",
        "questions": [
            {
                "text": "A solid sphere rolls without slipping down an incline of angle theta. Find its linear acceleration at the base.",
                "type": "Numerical", "marks": 4, "diff": "Hard", "year": 2024,
                "src": "Arihant JEE Main & Advanced Physics Chapterwise",
                "ans": "For rolling without slipping: a = (g * sin theta) / (1 + I / (m * R^2)). For a solid sphere, I = (2/5) * m * R^2. Thus a = (g * sin theta) / (1 + 2/5) = (5/7) * g * sin theta."
            }
        ]
    },
    {
        "exam_slug": "jee", "std": "JEE", "subj_name": "Mathematics",
        "board": "NTA / JEE Advanced / Arihant", "num": 2, "title": "Definite Integrals and Applications of Calculus",
        "weightage": "8-12 Marks",
        "summary": "Fundamental theorem of calculus, properties of definite integrals, King's rule, Leibniz rule for differentiating integrals, area under curves.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2012/Mathematics/lemh107.pdf",
        "questions": [
            {
                "text": "Evaluate the integral I = int_0^(pi/2) [sqrt(sin x) / (sqrt(sin x) + sqrt(cos x))] dx.",
                "type": "Numerical", "marks": 4, "diff": "Medium", "year": 2024,
                "src": "JEE Main Official Past Year Paper",
                "ans": "Using King's property int_0^a f(x) dx = int_0^a f(a - x) dx: I = int_0^(pi/2) [sqrt(cos x) / (sqrt(cos x) + sqrt(sin x))] dx. Adding the two expressions gives 2I = int_0^(pi/2) 1 dx = [x]_0^(pi/2) = pi/2. Therefore I = pi/4."
            }
        ]
    },

    # ── NEET UG (Subject: Biology - ID 85) ────────────────────────────────────
    {
        "exam_slug": "neet", "std": "NEET", "subj_name": "Biology",
        "board": "NTA / NEET / MTG", "num": 1, "title": "Principles of Inheritance and Variation (Genetics)",
        "weightage": "12-16 Marks (3-4 Questions)",
        "summary": "Mendel's laws of inheritance, monohybrid and dihybrid crosses, incomplete dominance, codominance, chromosomal theory, linkage and recombination, sex determination, pedigree analysis, genetic disorders (Mendelian and Chromosomal).",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2012/Biology/lebo105.pdf",
        "questions": [
            {
                "text": "What is the expected phenotypic ratio in the F2 generation of a dihybrid cross obeying Mendel's Law of Independent Assortment?",
                "type": "MCQ", "marks": 4, "diff": "Easy", "year": 2024,
                "src": "MTG NEET Champion Biology Chapterwise",
                "ans": "The classical phenotypic ratio for a dihybrid cross in F2 generation is 9 : 3 : 3 : 1 (Round Yellow : Round Green : Wrinkled Yellow : Wrinkled Green)."
            },
            {
                "text": "Distinguish between Klinefelter's syndrome and Turner's syndrome in terms of karyotype and sex chromosome composition.",
                "type": "Short Answer", "marks": 4, "diff": "Medium", "year": 2023,
                "src": "NEET UG Official Examination Paper",
                "ans": "Klinefelter's syndrome: Karyotype 47, XXY (an extra X chromosome in males leading to gynaecomastia and sterility). Turner's syndrome: Karyotype 45, X0 (monosomy of X chromosome in females with rudimentary ovaries and lack of secondary sexual characteristics)."
            }
        ]
    },

    # ── UPSC CIVIL SERVICES (Subject: General Studies - ID 1) ────────────────
    {
        "exam_slug": "upsc", "std": "UPSC", "subj_name": "General Studies",
        "board": "UPSC / Disha Publications", "num": 1, "title": "Modern Indian History & Freedom Struggle (1857-1947)",
        "weightage": "15-20 Marks in Prelims & Mains",
        "summary": "Revolt of 1857, socio-religious reform movements, Indian National Congress foundation, Swadeshi movement, Home Rule, Non-Cooperation, Civil Disobedience, Quit India, Cabinet Mission, Partition and Independence.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2012/History/lehs303.pdf",
        "questions": [
            {
                "text": "With reference to 8th August 1942 in Indian history, which one of the following statements is correct? (a) The Quit India Resolution was adopted by the AICC. (b) The Viceroy's Executive Council was expanded. (c) Constituent Assembly was convened. (d) Cripps Mission proposed Dominion status.",
                "type": "MCQ", "marks": 2, "diff": "Medium", "year": 2021,
                "src": "UPSC Civil Services Prelims Official Paper (Disha Compendium)",
                "ans": "Correct option is (a). On 8th August 1942, Mahatma Gandhi launched the Quit India Movement at the Bombay session of the All-India Congress Committee (AICC) at Gowalia Tank Maidan with the call 'Do or Die'."
            },
            {
                "text": "Explain how the Non-Cooperation Movement of 1920 represented a new watershed in the mass mobilization of India's anti-colonial struggle.",
                "type": "Long Answer", "marks": 10, "diff": "Hard", "year": 2024,
                "src": "UPSC Mains General Studies Paper 1 Archive",
                "ans": "Non-Cooperation transformed nationalism from an elite, middle-class discourse into a nationwide mass movement involving peasants, workers, students, and women across urban and rural India, uniting Hindu-Muslim fronts via the Khilafat platform and introducing boycott of colonial institutions."
            }
        ]
    },
    {
        "exam_slug": "upsc", "std": "UPSC", "subj_name": "General Studies",
        "board": "UPSC / Disha Publications", "num": 2, "title": "Indian Polity & Constitutional Framework",
        "weightage": "25-30 Marks in Prelims",
        "summary": "Preamble, Fundamental Rights (Articles 12-35), Directive Principles of State Policy, Fundamental Duties, Parliament, Supreme Court, Federalism, and Constitutional Amendments.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2011/Political%20Science/keps201.pdf",
        "questions": [
            {
                "text": "Which Article of the Constitution of India safeguards one's right to marry the person of one's choice? (a) Article 19 (b) Article 21 (c) Article 25 (d) Article 29.",
                "type": "MCQ", "marks": 2, "diff": "Easy", "year": 2019,
                "src": "UPSC Civil Services Prelims Official Paper",
                "ans": "Correct answer is (b) Article 21 (Right to Life and Personal Liberty). The Supreme Court upheld the right to marry a person of one's choice as an integral part of Article 21 in the Shafin Jahan v. Asokan K.M. (Hadiya case, 2018)."
            }
        ]
    },

    # ── TNPSC (Subject: General Studies - ID 1, General Tamil - ID 128) ───────
    {
        "exam_slug": "tnpsc", "std": "TNPSC", "subj_name": "General Studies",
        "board": "TNPSC / Samacheer Kalvi", "num": 8, "title": "Unit 8: History, Culture, Heritage & Socio-Political Movements in Tamil Nadu",
        "weightage": "30-40 Questions in Group 1 & Group 2",
        "summary": "History of Tamil Society, archaeological discoveries (Keezhadi, Kodumanal), Sangam Literature, Thirukkural (secular nature, relevance to modern governance), Justice Party, Self-Respect Movement, Dravidian Movement, and social welfare leaders.",
        "textbook_url": "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/Class%2010/Social%20Science/jess301.pdf",
        "questions": [
            {
                "text": "Which sangam port site on the Vaigai river has yielded extensive graffiti symbols, punch-marked silver coins, and brick structures dating back to 6th century BCE?",
                "type": "MCQ", "marks": 1.5, "diff": "Medium", "year": 2024,
                "src": "TNPSC Group 1 Prelims Official Paper",
                "ans": "Keezhadi (Sivagangai district), excavated by the Tamil Nadu State Department of Archaeology and ASI, establishes an urban civilization in Tamil Nadu contemporaneous with the Second Urbanization of the Gangetic valley."
            },
            {
                "text": "Explain Thirukkural's philosophy on good governance and righteous leadership as articulated in 'Iraimaatchi' (The Greatness of a King).",
                "type": "Short Answer", "marks": 5, "diff": "Medium", "year": 2022,
                "src": "TNPSC Group 2 Mains Official Archive",
                "ans": "In 'Iraimaatchi' (Kural 381-390), Valluvar states that a righteous sovereign is one who acquires wealth legally, stores it securely, protects it vigilantly, and redistributes it justly for public welfare: 'Iyatralum Eattalun Kaaththalum Kaatha Vakuththalum Vallath Arasu'."
            }
        ]
    }
]


def harvest_lessons():
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()

        # Subject map name -> id
        cur.execute("SELECT id, name FROM subjects")
        subj_map = {row["name"].lower(): row["id"] for row in cur.fetchall()}

        # Textbook map title -> id
        cur.execute("SELECT id, title FROM textbooks")
        tb_map = {row["title"].lower(): row["id"] for row in cur.fetchall()}

        ch_inserted = 0
        q_inserted = 0

        for ch in CHAPTERS_DATA:
            s_id = subj_map.get(ch["subj_name"].lower())
            if not s_id:
                print(f"Subject '{ch['subj_name']}' not found in DB! Skipping.")
                continue

            # Check if chapter exists
            cur.execute("""
                SELECT id FROM chapters
                WHERE exam_slug = %s AND standard_level = %s AND subject_id = %s AND chapter_number = %s
            """, (ch["exam_slug"], ch["std"], s_id, ch["num"]))
            existing_ch = cur.fetchone()

            if existing_ch:
                chapter_id = existing_ch["id"]
                cur.execute("""
                    UPDATE chapters
                    SET chapter_title = %s, board = %s, textbook_chapter_url = %s,
                        summary_notes = %s, marks_weightage = %s
                    WHERE id = %s
                """, (ch["title"], ch["board"], ch["textbook_url"], ch["summary"], ch["weightage"], chapter_id))
            else:
                cur.execute("""
                    INSERT INTO chapters (
                        exam_slug, standard_level, subject_id, board, chapter_number,
                        chapter_title, textbook_chapter_url, summary_notes, marks_weightage
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ch["exam_slug"], ch["std"], s_id, ch["board"], ch["num"],
                    ch["title"], ch["textbook_url"], ch["summary"], ch["weightage"]
                ))
                chapter_id = cur.lastrowid
                ch_inserted += 1

            # Insert curated questions for this chapter
            for q in ch.get("questions", []):
                cur.execute("""
                    SELECT id FROM chapter_questions
                    WHERE chapter_id = %s AND question_text = %s
                """, (chapter_id, q["text"]))
                existing_q = cur.fetchone()

                if not existing_q:
                    cur.execute("""
                        INSERT INTO chapter_questions (
                            chapter_id, question_text, question_type, marks,
                            answer_explanation, source_publication, difficulty, year
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        chapter_id, q["text"], q["type"], q["marks"],
                        q["ans"], q["src"], q["diff"], q.get("year", 2024)
                    ))
                    q_inserted += 1

        conn.commit()

        # Count totals
        cur.execute("SELECT COUNT(*) AS cnt FROM chapters")
        total_ch = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) AS cnt FROM chapter_questions")
        total_q = cur.fetchone()["cnt"]

        print(f"Lesson Harvest Complete! Chapters inserted: {ch_inserted}, Questions inserted: {q_inserted}")
        print(f"Total Database Lessons: {total_ch} | Total Lesson Questions: {total_q}")


if __name__ == "__main__":
    harvest_lessons()
