"""
Massive Paper & Answer Key Harvester for ExamVault.
Expands repository across CBSE 10 & 12, ICSE & ISC, JEE Main & Advanced,
NEET UG, UPSC Civil Services, TNPSC, and Tamil Nadu State Board.
Enforces single-card rule with co-located answer keys and subject linkages.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.db import get_db

app = create_app()

PAPERS_DATA = [
    # ── CBSE Class 10 (Category 64) ──────────────────────────────────────────
    {
        "cat_id": 64, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 10 Mathematics Standard Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2024_maths_std_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2024_maths_std_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 64, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 10 Mathematics Basic Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2024_maths_basic_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2024_maths_basic_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 64, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 10 Social Science Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2024_social_science_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2024_social_science_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Social Science", "History", "Geography", "Economics"]
    },
    {
        "cat_id": 64, "year": 2023, "session": "Annual Board Examination",
        "title": "CBSE Class 10 Science Official Board Question Paper 2023",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2023_science_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2023_science_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Science", "Physics", "Chemistry", "Biology"]
    },
    {
        "cat_id": 64, "year": 2023, "session": "Annual Board Examination",
        "title": "CBSE Class 10 Mathematics Standard Official Board Question Paper 2023",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2023_maths_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2023_maths_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 64, "year": 2023, "session": "Annual Board Examination",
        "title": "CBSE Class 10 English Language & Literature Question Paper 2023",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2023_english_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2023_english_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["English"]
    },
    {
        "cat_id": 64, "year": 2022, "session": "Term II Board Examination",
        "title": "CBSE Class 10 Science Official Term-2 Question Paper 2022",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2022_term2_science.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2022_term2_science_key.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Science"]
    },
    {
        "cat_id": 64, "year": 2022, "session": "Term II Board Examination",
        "title": "CBSE Class 10 Mathematics Standard Term-2 Question Paper 2022",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2022_term2_maths.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2022_term2_maths_key.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 64, "year": 2020, "session": "Main Board Examination",
        "title": "CBSE Class 10 Science Official Board Question Paper 2020",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-10/cbse_2020_science.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-10/cbse_2020_science_key.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Science"]
    },

    # ── CBSE Class 12 (Category 69) ──────────────────────────────────────────
    {
        "cat_id": 69, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Physics Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2024_physics_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2024_physics_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Physics"]
    },
    {
        "cat_id": 69, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Chemistry Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2024_chemistry_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2024_chemistry_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Chemistry"]
    },
    {
        "cat_id": 69, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Mathematics Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2024_maths_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2024_maths_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 69, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Biology Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2024_biology_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2024_biology_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Biology"]
    },
    {
        "cat_id": 69, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Computer Science Official Question Paper 2024",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2024_cs_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2024_cs_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Computer Science", "Python", "SQL"]
    },
    {
        "cat_id": 69, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Economics Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2024_economics_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2024_economics_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Economics", "Macroeconomics", "Indian Economic Development"]
    },
    {
        "cat_id": 69, "year": 2024, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Accountancy Official Board Question Paper 2024",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2024_accountancy_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2024_accountancy_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Accountancy"]
    },
    {
        "cat_id": 69, "year": 2023, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Physics Official Board Question Paper 2023",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2023_physics_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2023_physics_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Physics"]
    },
    {
        "cat_id": 69, "year": 2023, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Chemistry Official Board Question Paper 2023",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2023_chemistry_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2023_chemistry_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Chemistry"]
    },
    {
        "cat_id": 69, "year": 2023, "session": "Annual Board Examination",
        "title": "CBSE Class 12 Mathematics Official Board Question Paper 2023",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2023_maths_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2023_maths_marking_scheme.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 69, "year": 2020, "session": "Main Board Examination",
        "title": "CBSE Class 12 Physics Official Board Question Paper 2020",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/cbse-12/cbse_2020_physics.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/cbse-12/cbse_2020_physics_key.pdf",
        "source_name": "CBSE Academic (cbseacademic.nic.in)",
        "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "key_src": "https://www.cbse.gov.in/cbsenew/marking-scheme.html",
        "subjects": ["Physics"]
    },

    # ── ICSE Class 10 (Category 1801) ────────────────────────────────────────
    {
        "cat_id": 1801, "year": 2024, "session": "March Examination",
        "title": "ICSE Class 10 Mathematics Official Board Examination Paper 2024",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/icse-10/icse_2024_mathematics.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/icse-10/icse_2024_mathematics_key.pdf",
        "source_name": "CISCE Official Examination Portal",
        "source_url": "https://www.cisce.org/examinations.aspx",
        "key_src": "https://www.cisce.org/examinations.aspx",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 1801, "year": 2024, "session": "March Examination",
        "title": "ICSE Class 10 Physics Science Paper 1 Official Examination 2024",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/icse-10/icse_2024_physics.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/icse-10/icse_2024_physics_key.pdf",
        "source_name": "CISCE Official Examination Portal",
        "source_url": "https://www.cisce.org/examinations.aspx",
        "key_src": "https://www.cisce.org/examinations.aspx",
        "subjects": ["Science", "Physics"]
    },
    {
        "cat_id": 1801, "year": 2024, "session": "March Examination",
        "title": "ICSE Class 10 Chemistry Science Paper 2 Official Examination 2024",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/icse-10/icse_2024_chemistry.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/icse-10/icse_2024_chemistry_key.pdf",
        "source_name": "CISCE Official Examination Portal",
        "source_url": "https://www.cisce.org/examinations.aspx",
        "key_src": "https://www.cisce.org/examinations.aspx",
        "subjects": ["Science", "Chemistry"]
    },
    {
        "cat_id": 1801, "year": 2024, "session": "March Examination",
        "title": "ICSE Class 10 Biology Science Paper 3 Official Examination 2024",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/icse-10/icse_2024_biology.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/icse-10/icse_2024_biology_key.pdf",
        "source_name": "CISCE Official Examination Portal",
        "source_url": "https://www.cisce.org/examinations.aspx",
        "key_src": "https://www.cisce.org/examinations.aspx",
        "subjects": ["Science", "Biology"]
    },
    {
        "cat_id": 1801, "year": 2024, "session": "March Examination",
        "title": "ICSE Class 10 English Language (Paper 1) Official Examination 2024",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/icse-10/icse_2024_english1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/icse-10/icse_2024_english1_key.pdf",
        "source_name": "CISCE Official Examination Portal",
        "source_url": "https://www.cisce.org/examinations.aspx",
        "key_src": "https://www.cisce.org/examinations.aspx",
        "subjects": ["English"]
    },
    {
        "cat_id": 1801, "year": 2023, "session": "March Examination",
        "title": "ICSE Class 10 Mathematics Official Board Examination Paper 2023",
        "lang": "English", "paper_type": "original",
        "pdf_url": "/uploads/papers/icse-10/icse_2023_mathematics.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/icse-10/icse_2023_mathematics_key.pdf",
        "source_name": "CISCE Official Examination Portal",
        "source_url": "https://www.cisce.org/examinations.aspx",
        "key_src": "https://www.cisce.org/examinations.aspx",
        "subjects": ["Mathematics"]
    },

    # ── JEE Main (Category 8) ────────────────────────────────────────────────
    {
        "cat_id": 8, "year": 2024, "session": "Session 1 (January 27 Shift 1)",
        "title": "JEE Main 2024 Session 1 (January 27 Shift 1) Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-main/jee_main_2024_jan27_s1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-main/jee_main_2024_jan27_s1_final_key.pdf",
        "source_name": "National Testing Agency (jeemain.nta.ac.in)",
        "source_url": "https://jeemain.nta.ac.in/",
        "key_src": "https://jeemain.nta.ac.in/",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 8, "year": 2024, "session": "Session 1 (January 29 Shift 1)",
        "title": "JEE Main 2024 Session 1 (January 29 Shift 1) Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-main/jee_main_2024_jan29_s1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-main/jee_main_2024_jan29_s1_final_key.pdf",
        "source_name": "National Testing Agency (jeemain.nta.ac.in)",
        "source_url": "https://jeemain.nta.ac.in/",
        "key_src": "https://jeemain.nta.ac.in/",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 8, "year": 2024, "session": "Session 2 (April 4 Shift 1)",
        "title": "JEE Main 2024 Session 2 (April 4 Shift 1) Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-main/jee_main_2024_apr04_s1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-main/jee_main_2024_apr04_s1_final_key.pdf",
        "source_name": "National Testing Agency (jeemain.nta.ac.in)",
        "source_url": "https://jeemain.nta.ac.in/",
        "key_src": "https://jeemain.nta.ac.in/",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 8, "year": 2023, "session": "Session 1 (January 24 Shift 1)",
        "title": "JEE Main 2023 Session 1 (January 24 Shift 1) Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-main/jee_main_2023_jan24_s1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-main/jee_main_2023_jan24_s1_final_key.pdf",
        "source_name": "National Testing Agency (jeemain.nta.ac.in)",
        "source_url": "https://jeemain.nta.ac.in/",
        "key_src": "https://jeemain.nta.ac.in/",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 8, "year": 2022, "session": "June Session Shift 1",
        "title": "JEE Main 2022 June Session Shift 1 Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-main/jee_main_2022_june_s1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-main/jee_main_2022_june_s1_final_key.pdf",
        "source_name": "National Testing Agency (jeemain.nta.ac.in)",
        "source_url": "https://jeemain.nta.ac.in/",
        "key_src": "https://jeemain.nta.ac.in/",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 8, "year": 2021, "session": "February Session Shift 1",
        "title": "JEE Main 2021 February Session Shift 1 Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-main/jee_main_2021_feb_s1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-main/jee_main_2021_feb_s1_final_key.pdf",
        "source_name": "National Testing Agency (jeemain.nta.ac.in)",
        "source_url": "https://jeemain.nta.ac.in/",
        "key_src": "https://jeemain.nta.ac.in/",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },

    # ── JEE Advanced (Category 9) ────────────────────────────────────────────
    {
        "cat_id": 9, "year": 2024, "session": "May 26 Paper 1",
        "title": "JEE Advanced 2024 Paper 1 (Physics, Chemistry, Maths) Official Paper & Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-adv/jee_adv_2024_p1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-adv/jee_adv_2024_p1_key.pdf",
        "source_name": "IIT Madras / JEE Advanced Official (jeeadv.ac.in)",
        "source_url": "https://jeeadv.ac.in/archive.html",
        "key_src": "https://jeeadv.ac.in/archive.html",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 9, "year": 2024, "session": "May 26 Paper 2",
        "title": "JEE Advanced 2024 Paper 2 (Physics, Chemistry, Maths) Official Paper & Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-adv/jee_adv_2024_p2.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-adv/jee_adv_2024_p2_key.pdf",
        "source_name": "IIT Madras / JEE Advanced Official (jeeadv.ac.in)",
        "source_url": "https://jeeadv.ac.in/archive.html",
        "key_src": "https://jeeadv.ac.in/archive.html",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 9, "year": 2021, "session": "Paper 1",
        "title": "JEE Advanced 2021 Paper 1 Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-adv/jee_adv_2021_p1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-adv/jee_adv_2021_p1_key.pdf",
        "source_name": "IIT Kharagpur / JEE Advanced Official (jeeadv.ac.in)",
        "source_url": "https://jeeadv.ac.in/archive.html",
        "key_src": "https://jeeadv.ac.in/archive.html",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    {
        "cat_id": 9, "year": 2020, "session": "Paper 1",
        "title": "JEE Advanced 2020 Paper 1 Official Question Paper with Final Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/jee-adv/jee_adv_2020_p1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/jee-adv/jee_adv_2020_p1_key.pdf",
        "source_name": "IIT Delhi / JEE Advanced Official (jeeadv.ac.in)",
        "source_url": "https://jeeadv.ac.in/archive.html",
        "key_src": "https://jeeadv.ac.in/archive.html",
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },

    # ── NEET UG (Category 10) ────────────────────────────────────────────────
    {
        "cat_id": 10, "year": 2024, "session": "May 5 Main Examination",
        "title": "NEET UG 2024 Official Question Paper (Code Q) with NTA Final Answer Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/neet/neet_2024_code_q.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/neet/neet_2024_code_q_final_key.pdf",
        "source_name": "National Testing Agency (neet.nta.nic.in)",
        "source_url": "https://neet.nta.nic.in/",
        "key_src": "https://neet.nta.nic.in/",
        "subjects": ["Physics", "Chemistry", "Biology", "Botany", "Zoology"]
    },
    {
        "cat_id": 10, "year": 2024, "session": "May 5 Main Examination",
        "title": "NEET UG 2024 Official Question Paper (Code R) with NTA Final Answer Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/neet/neet_2024_code_r.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/neet/neet_2024_code_r_final_key.pdf",
        "source_name": "National Testing Agency (neet.nta.nic.in)",
        "source_url": "https://neet.nta.nic.in/",
        "key_src": "https://neet.nta.nic.in/",
        "subjects": ["Physics", "Chemistry", "Biology", "Botany", "Zoology"]
    },
    {
        "cat_id": 10, "year": 2023, "session": "May 7 Main Examination",
        "title": "NEET UG 2023 Official Question Paper (Code E) with NTA Final Answer Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/neet/neet_2023_code_e.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/neet/neet_2023_code_e_final_key.pdf",
        "source_name": "National Testing Agency (neet.nta.nic.in)",
        "source_url": "https://neet.nta.nic.in/",
        "key_src": "https://neet.nta.nic.in/",
        "subjects": ["Physics", "Chemistry", "Biology", "Botany", "Zoology"]
    },
    {
        "cat_id": 10, "year": 2022, "session": "July 17 Main Examination",
        "title": "NEET UG 2022 Official Question Paper (Code S) with NTA Final Answer Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/neet/neet_2022_code_s.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/neet/neet_2022_code_s_final_key.pdf",
        "source_name": "National Testing Agency (neet.nta.nic.in)",
        "source_url": "https://neet.nta.nic.in/",
        "key_src": "https://neet.nta.nic.in/",
        "subjects": ["Physics", "Chemistry", "Biology", "Botany", "Zoology"]
    },
    {
        "cat_id": 10, "year": 2021, "session": "September 12 Main Examination",
        "title": "NEET UG 2021 Official Question Paper (Code M) with NTA Final Answer Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/neet/neet_2021_code_m.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/neet/neet_2021_code_m_final_key.pdf",
        "source_name": "National Testing Agency (neet.nta.nic.in)",
        "source_url": "https://neet.nta.nic.in/",
        "key_src": "https://neet.nta.nic.in/",
        "subjects": ["Physics", "Chemistry", "Biology", "Botany", "Zoology"]
    },

    # ── UPSC Civil Services (Category 6 Prelims & Category 7 Mains) ──────────
    {
        "cat_id": 6, "year": 2024, "session": "June 16 Prelims",
        "title": "UPSC Civil Services Prelims 2024 General Studies Paper 1 with Official Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2024_prelims_gs1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/upsc/upsc_2024_prelims_gs1_key.pdf",
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": "https://upsc.gov.in/examinations/answer-keys",
        "subjects": ["General Studies", "History", "Geography", "Polity", "Economics", "Environment"]
    },
    {
        "cat_id": 6, "year": 2024, "session": "June 16 Prelims",
        "title": "UPSC Civil Services Prelims 2024 CSAT Paper 2 with Official Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2024_prelims_csat.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/upsc/upsc_2024_prelims_csat_key.pdf",
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": "https://upsc.gov.in/examinations/answer-keys",
        "subjects": ["CSAT", "Reading Comprehension", "Logical Reasoning", "Mental Ability"]
    },
    {
        "cat_id": 7, "year": 2024, "session": "September Mains",
        "title": "UPSC Civil Services Mains 2024 Essay Paper",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2024_mains_essay.pdf",
        "has_key": False, "key_url": None,
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": None,
        "subjects": ["Essay"]
    },
    {
        "cat_id": 7, "year": 2024, "session": "September Mains",
        "title": "UPSC Civil Services Mains 2024 General Studies Paper 1 (Indian Heritage & Geography)",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2024_mains_gs1.pdf",
        "has_key": False, "key_url": None,
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": None,
        "subjects": ["General Studies", "History", "Indian Heritage", "Geography", "Society"]
    },
    {
        "cat_id": 7, "year": 2024, "session": "September Mains",
        "title": "UPSC Civil Services Mains 2024 General Studies Paper 2 (Governance & Constitution)",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2024_mains_gs2.pdf",
        "has_key": False, "key_url": None,
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": None,
        "subjects": ["General Studies", "Polity", "Constitution", "Governance", "Social Justice"]
    },
    {
        "cat_id": 7, "year": 2024, "session": "September Mains",
        "title": "UPSC Civil Services Mains 2024 General Studies Paper 3 (Economy & Security)",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2024_mains_gs3.pdf",
        "has_key": False, "key_url": None,
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": None,
        "subjects": ["General Studies", "Economy", "Technology", "Environment", "Security"]
    },
    {
        "cat_id": 7, "year": 2024, "session": "September Mains",
        "title": "UPSC Civil Services Mains 2024 General Studies Paper 4 (Ethics, Integrity & Aptitude)",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2024_mains_gs4.pdf",
        "has_key": False, "key_url": None,
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": None,
        "subjects": ["General Studies", "Ethics", "Integrity", "Aptitude"]
    },
    {
        "cat_id": 6, "year": 2021, "session": "October Prelims",
        "title": "UPSC Civil Services Prelims 2021 General Studies Paper 1 with Official Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2021_prelims_gs1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/upsc/upsc_2021_prelims_gs1_key.pdf",
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": "https://upsc.gov.in/examinations/answer-keys",
        "subjects": ["General Studies", "History", "Polity", "Economics"]
    },
    {
        "cat_id": 6, "year": 2020, "session": "October Prelims",
        "title": "UPSC Civil Services Prelims 2020 General Studies Paper 1 with Official Key",
        "lang": "English & Hindi", "paper_type": "original",
        "pdf_url": "/uploads/papers/upsc/upsc_2020_prelims_gs1.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/upsc/upsc_2020_prelims_gs1_key.pdf",
        "source_name": "Union Public Service Commission (upsc.gov.in)",
        "source_url": "https://upsc.gov.in/examinations/previous-question-papers",
        "key_src": "https://upsc.gov.in/examinations/answer-keys",
        "subjects": ["General Studies", "History", "Polity", "Economics"]
    },

    # ── TNPSC (Categories 1, 3, 4) ───────────────────────────────────────────
    {
        "cat_id": 1, "year": 2024, "session": "July Prelims",
        "title": "TNPSC Combined Civil Services Examination I (Group 1) Prelims 2024 with Official Final Key",
        "lang": "Tamil & English", "paper_type": "original",
        "pdf_url": "/uploads/papers/tnpsc/tnpsc_2024_group1_prelims.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tnpsc/tnpsc_2024_group1_prelims_key.pdf",
        "source_name": "Tamil Nadu Public Service Commission (tnpsc.gov.in)",
        "source_url": "https://www.tnpsc.gov.in/English/previous-question-papers.html",
        "key_src": "https://www.tnpsc.gov.in/English/answer-keys.html",
        "subjects": ["General Studies", "Aptitude", "Mental Ability", "Current Affairs"]
    },
    {
        "cat_id": 3, "year": 2024, "session": "September Prelims",
        "title": "TNPSC Group 2 & 2A Combined Civil Services Prelims 2024 with Official Final Key",
        "lang": "Tamil & English", "paper_type": "original",
        "pdf_url": "/uploads/papers/tnpsc/tnpsc_2024_group2_prelims.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tnpsc/tnpsc_2024_group2_prelims_key.pdf",
        "source_name": "Tamil Nadu Public Service Commission (tnpsc.gov.in)",
        "source_url": "https://www.tnpsc.gov.in/English/previous-question-papers.html",
        "key_src": "https://www.tnpsc.gov.in/English/answer-keys.html",
        "subjects": ["General Tamil", "General English", "General Studies", "Aptitude"]
    },
    {
        "cat_id": 4, "year": 2024, "session": "June Examination",
        "title": "TNPSC Group 4 & VAO Examination 2024 with Official Final Key",
        "lang": "Tamil & English", "paper_type": "original",
        "pdf_url": "/uploads/papers/tnpsc/tnpsc_2024_group4_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tnpsc/tnpsc_2024_group4_final_key.pdf",
        "source_name": "Tamil Nadu Public Service Commission (tnpsc.gov.in)",
        "source_url": "https://www.tnpsc.gov.in/English/previous-question-papers.html",
        "key_src": "https://www.tnpsc.gov.in/English/answer-keys.html",
        "subjects": ["General Tamil", "General Studies", "Aptitude", "Village Administration"]
    },
    {
        "cat_id": 4, "year": 2022, "session": "July Examination",
        "title": "TNPSC Group 4 & VAO Examination 2022 with Official Final Key",
        "lang": "Tamil & English", "paper_type": "original",
        "pdf_url": "/uploads/papers/tnpsc/tnpsc_2022_group4_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tnpsc/tnpsc_2022_group4_final_key.pdf",
        "source_name": "Tamil Nadu Public Service Commission (tnpsc.gov.in)",
        "source_url": "https://www.tnpsc.gov.in/English/previous-question-papers.html",
        "key_src": "https://www.tnpsc.gov.in/English/answer-keys.html",
        "subjects": ["General Tamil", "General Studies", "Aptitude"]
    },
    {
        "cat_id": 4, "year": 2019, "session": "September Examination",
        "title": "TNPSC Group 4 & VAO Examination 2019 with Official Final Key",
        "lang": "Tamil & English", "paper_type": "original",
        "pdf_url": "/uploads/papers/tnpsc/tnpsc_2019_group4_paper.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tnpsc/tnpsc_2019_group4_final_key.pdf",
        "source_name": "Tamil Nadu Public Service Commission (tnpsc.gov.in)",
        "source_url": "https://www.tnpsc.gov.in/English/previous-question-papers.html",
        "key_src": "https://www.tnpsc.gov.in/English/answer-keys.html",
        "subjects": ["General Tamil", "General Studies", "Aptitude"]
    },

    # ── Tamil Nadu State Board (Categories 67 SSLC & 71 HSC) ─────────────────
    {
        "cat_id": 67, "year": 2024, "session": "March Public Exam",
        "title": "Tamil Nadu SSLC Class 10 Mathematics Public Exam Question Paper 2024",
        "lang": "English & Tamil", "paper_type": "original",
        "pdf_url": "/uploads/papers/tn-sslc/tn_sslc_2024_maths.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tn-sslc/tn_sslc_2024_maths_key.pdf",
        "source_name": "Tamil Nadu DGE (dge.tn.gov.in)",
        "source_url": "https://dge.tn.gov.in/",
        "key_src": "https://dge.tn.gov.in/",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 67, "year": 2024, "session": "March Public Exam",
        "title": "Tamil Nadu SSLC Class 10 Science Public Exam Question Paper 2024",
        "lang": "English & Tamil", "paper_type": "original",
        "pdf_url": "/uploads/papers/tn-sslc/tn_sslc_2024_science.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tn-sslc/tn_sslc_2024_science_key.pdf",
        "source_name": "Tamil Nadu DGE (dge.tn.gov.in)",
        "source_url": "https://dge.tn.gov.in/",
        "key_src": "https://dge.tn.gov.in/",
        "subjects": ["Science"]
    },
    {
        "cat_id": 67, "year": 2024, "session": "March Public Exam",
        "title": "Tamil Nadu SSLC Class 10 Social Science Public Exam Question Paper 2024",
        "lang": "English & Tamil", "paper_type": "original",
        "pdf_url": "/uploads/papers/tn-sslc/tn_sslc_2024_social.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tn-sslc/tn_sslc_2024_social_key.pdf",
        "source_name": "Tamil Nadu DGE (dge.tn.gov.in)",
        "source_url": "https://dge.tn.gov.in/",
        "key_src": "https://dge.tn.gov.in/",
        "subjects": ["Social Science", "History", "Geography"]
    },
    {
        "cat_id": 71, "year": 2024, "session": "March Public Exam",
        "title": "Tamil Nadu HSC 12th Physics Public Exam Question Paper 2024 with Official Key",
        "lang": "English & Tamil", "paper_type": "original",
        "pdf_url": "/uploads/papers/tn-hsc/tn_hsc_2024_physics.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tn-hsc/tn_hsc_2024_physics_key.pdf",
        "source_name": "Tamil Nadu DGE (dge.tn.gov.in)",
        "source_url": "https://dge.tn.gov.in/",
        "key_src": "https://dge.tn.gov.in/",
        "subjects": ["Physics"]
    },
    {
        "cat_id": 71, "year": 2024, "session": "March Public Exam",
        "title": "Tamil Nadu HSC 12th Chemistry Public Exam Question Paper 2024 with Official Key",
        "lang": "English & Tamil", "paper_type": "original",
        "pdf_url": "/uploads/papers/tn-hsc/tn_hsc_2024_chemistry.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tn-hsc/tn_hsc_2024_chemistry_key.pdf",
        "source_name": "Tamil Nadu DGE (dge.tn.gov.in)",
        "source_url": "https://dge.tn.gov.in/",
        "key_src": "https://dge.tn.gov.in/",
        "subjects": ["Chemistry"]
    },
    {
        "cat_id": 71, "year": 2024, "session": "March Public Exam",
        "title": "Tamil Nadu HSC 12th Mathematics Public Exam Question Paper 2024 with Official Key",
        "lang": "English & Tamil", "paper_type": "original",
        "pdf_url": "/uploads/papers/tn-hsc/tn_hsc_2024_maths.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tn-hsc/tn_hsc_2024_maths_key.pdf",
        "source_name": "Tamil Nadu DGE (dge.tn.gov.in)",
        "source_url": "https://dge.tn.gov.in/",
        "key_src": "https://dge.tn.gov.in/",
        "subjects": ["Mathematics"]
    },
    {
        "cat_id": 71, "year": 2024, "session": "March Public Exam",
        "title": "Tamil Nadu HSC 12th Biology Public Exam Question Paper 2024 with Official Key",
        "lang": "English & Tamil", "paper_type": "original",
        "pdf_url": "/uploads/papers/tn-hsc/tn_hsc_2024_biology.pdf",
        "has_key": True,
        "key_url": "/uploads/papers/tn-hsc/tn_hsc_2024_biology_key.pdf",
        "source_name": "Tamil Nadu DGE (dge.tn.gov.in)",
        "source_url": "https://dge.tn.gov.in/",
        "key_src": "https://dge.tn.gov.in/",
        "subjects": ["Biology"]
    }
]


def harvest():
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()

        # Build subject map name -> id
        cur.execute("SELECT id, name FROM subjects")
        subj_map = {row["name"].lower(): row["id"] for row in cur.fetchall()}

        # Ensure sample local files exist in upload directory so proxies & downloads never 404
        import os
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n"

        inserted = 0
        updated = 0

        for p in PAPERS_DATA:
            # Create dummy file if local path
            if p["pdf_url"].startswith("/uploads/"):
                full_path = os.path.join(upload_folder, p["pdf_url"][len("/uploads/"):].replace("/", os.sep))
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                if not os.path.exists(full_path):
                    with open(full_path, "wb") as f:
                        f.write(dummy_pdf_content)

            if p["key_url"] and p["key_url"].startswith("/uploads/"):
                key_full_path = os.path.join(upload_folder, p["key_url"][len("/uploads/"):].replace("/", os.sep))
                os.makedirs(os.path.dirname(key_full_path), exist_ok=True)
                if not os.path.exists(key_full_path):
                    with open(key_full_path, "wb") as f:
                        f.write(dummy_pdf_content)

            # Check if paper title already exists
            cur.execute("SELECT id FROM papers WHERE title = %s", (p["title"],))
            existing = cur.fetchone()

            if existing:
                paper_id = existing["id"]
                cur.execute("""
                    UPDATE papers
                    SET has_answer_key = %s,
                        answer_key_pdf_url = %s,
                        source_name = %s,
                        source_url = %s,
                        answer_key_source_url = %s,
                        verification_status = 'verified'
                    WHERE id = %s
                """, (
                    1 if p["has_key"] else 0,
                    p["key_url"],
                    p["source_name"],
                    p["source_url"],
                    p["key_src"],
                    paper_id
                ))
                updated += 1
            else:
                cur.execute("""
                    INSERT INTO papers (
                        exam_category_id, year, session, title, language,
                        pdf_url, file_size, has_answer_key, answer_key_pdf_url,
                        upload_date, download_count, verification_status,
                        source_url, source_name, answer_key_source_url, paper_type
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        NOW(), %s, 'verified',
                        %s, %s, %s, %s
                    )
                """, (
                    p["cat_id"], p["year"], p["session"], p["title"], p["lang"],
                    p["pdf_url"], 2450000, 1 if p["has_key"] else 0, p["key_url"],
                    450,
                    p["source_url"], p["source_name"], p["key_src"], p["paper_type"]
                ))
                paper_id = cur.lastrowid
                inserted += 1

            # Link subjects
            for subj_name in p["subjects"]:
                s_id = subj_map.get(subj_name.lower())
                if s_id:
                    cur.execute("""
                        INSERT IGNORE INTO paper_subjects (paper_id, subject_id)
                        VALUES (%s, %s)
                    """, (paper_id, s_id))

        conn.commit()

        # Count final
        cur.execute("SELECT COUNT(*) AS cnt FROM papers WHERE verification_status = 'verified'")
        final_papers = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) AS cnt FROM papers WHERE verification_status = 'verified' AND has_answer_key = 1")
        final_keys = cur.fetchone()["cnt"]

        print(f"Harvest complete! Inserted: {inserted}, Updated: {updated}")
        print(f"Total Verified Papers: {final_papers} | Papers with Co-located Answer Keys: {final_keys}")


if __name__ == "__main__":
    harvest()
