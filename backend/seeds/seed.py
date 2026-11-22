"""
ExamVault seed script — populates all 4 exams (TNPSC, UPSC, JEE, NEET)
with categories and 5+ papers per exam across multiple years.

Usage:
    cd backend
    python seeds/seed.py

Requires .env to be present (copies .env.example if needed).
"""
import sys
import os

# Allow running from anywhere inside the backend dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app import create_app
from app.extensions import db
from app.models.exam import Exam, ExamCategory
from app.models.paper import Paper, Subject
from app.models.user import User
import urllib.request

def ensure_sample_pdf():
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    pdf_path = os.path.join(upload_dir, 'sample.pdf')
    if not os.path.exists(pdf_path):
        print("  Downloading sample PDF for seeded papers...")
        url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        urllib.request.urlretrieve(url, pdf_path)
    return "/uploads/sample.pdf"

# ─────────────────────────────────────────────────────────────────────────────
# Seed data definition
# ─────────────────────────────────────────────────────────────────────────────

SEED_DATA = [
    # ── TNPSC ───────────────────────────────────────────────────────────────
    {
        "name": "TNPSC",
        "slug": "tnpsc",
        "description": (
            "Tamil Nadu Public Service Commission conducts recruitment examinations "
            "for various state government posts. TNPSC Group exams are among the most "
            "competitive state-level exams in India."
        ),
        "accent_color_hex": "#C1483A",
        "categories": [
            {
                "name": "Group 1",
                "slug": "group-1",
                "subjects": ["General Studies", "Aptitude & Mental Ability", "Tamil"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "TNPSC Group 1 Preliminary Examination 2019",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2456789,
                    },
                    {
                        "year": 2020,
                        "title": "TNPSC Group 1 Preliminary Examination 2020",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2378910,
                    },
                    {
                        "year": 2021,
                        "title": "TNPSC Group 1 Mains Paper I — General Studies 2021",
                        "language": "Tamil/English",
                        "has_answer_key": False,
                        "file_size": 3102456,
                    },
                    {
                        "year": 2022,
                        "title": "TNPSC Group 1 Preliminary Examination 2022",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2891234,
                    },
                    {
                        "year": 2023,
                        "title": "TNPSC Group 1 Preliminary Examination 2023",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2654321,
                    },
                ],
            },
            {
                "name": "Group 2",
                "slug": "group-2",
                "subjects": ["General Studies", "Aptitude & Mental Ability"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "TNPSC Group 2 Main Written Examination 2019",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 1987654,
                    },
                    {
                        "year": 2020,
                        "title": "TNPSC Group 2 (Non-Interview) Examination 2020",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2145678,
                    },
                    {
                        "year": 2022,
                        "title": "TNPSC Group 2A Main Examination 2022",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2345000,
                    },
                    {
                        "year": 2023,
                        "title": "TNPSC Group 2 Preliminary Examination 2023",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2198765,
                    },
                ],
            },
            {
                "name": "Group 4",
                "slug": "group-4",
                "subjects": ["General Studies", "Aptitude & Mental Ability", "Tamil"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "TNPSC Group 4 Examination 2019",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 1876543,
                    },
                    {
                        "year": 2021,
                        "title": "TNPSC Group 4 Examination 2021",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 1923456,
                    },
                    {
                        "year": 2022,
                        "title": "TNPSC Group 4 Examination 2022",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 2056789,
                    },
                    {
                        "year": 2023,
                        "title": "TNPSC Group 4 Examination 2023",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 1998765,
                    },
                ],
            },
            {
                "name": "VAO",
                "slug": "vao",
                "subjects": ["General Studies", "Tamil"],
                "papers": [
                    {
                        "year": 2020,
                        "title": "TNPSC VAO (Village Administrative Officer) Exam 2020",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 1765432,
                    },
                    {
                        "year": 2022,
                        "title": "TNPSC VAO Examination 2022",
                        "language": "Tamil/English",
                        "has_answer_key": True,
                        "file_size": 1854321,
                    },
                ],
            },
        ],
    },

    # ── UPSC ────────────────────────────────────────────────────────────────
    {
        "name": "UPSC",
        "slug": "upsc",
        "description": (
            "Union Public Service Commission conducts the Civil Services Examination "
            "— India's premier all-India competitive examination for IAS, IPS, IFS, "
            "and other Group A central services."
        ),
        "accent_color_hex": "#1F6F5C",
        "categories": [
            {
                "name": "Prelims — GS Paper I",
                "slug": "prelims-gs-1",
                "subjects": ["History", "Geography", "Polity", "Economy", "Environment", "Science & Technology"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "UPSC Civil Services Prelims GS Paper I 2019",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 3456789,
                    },
                    {
                        "year": 2020,
                        "title": "UPSC Civil Services Prelims GS Paper I 2020",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 3234567,
                    },
                    {
                        "year": 2021,
                        "title": "UPSC Civil Services Prelims GS Paper I 2021",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 3345678,
                    },
                    {
                        "year": 2022,
                        "title": "UPSC Civil Services Prelims GS Paper I 2022",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 3456000,
                    },
                    {
                        "year": 2023,
                        "title": "UPSC Civil Services Prelims GS Paper I 2023",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 3512345,
                    },
                ],
            },
            {
                "name": "Prelims — CSAT Paper II",
                "slug": "prelims-csat",
                "subjects": ["Comprehension", "Logical Reasoning", "Data Interpretation"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "UPSC CSAT Paper II 2019",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2876543,
                    },
                    {
                        "year": 2020,
                        "title": "UPSC CSAT Paper II 2020",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2987654,
                    },
                    {
                        "year": 2021,
                        "title": "UPSC CSAT Paper II 2021",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2765432,
                    },
                    {
                        "year": 2022,
                        "title": "UPSC CSAT Paper II 2022",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2898765,
                    },
                    {
                        "year": 2023,
                        "title": "UPSC CSAT Paper II 2023",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2934567,
                    },
                ],
            },
            {
                "name": "Mains — GS Paper I",
                "slug": "mains-gs-1",
                "subjects": ["History", "Indian Heritage & Culture", "World History", "Geography"],
                "papers": [
                    {
                        "year": 2021,
                        "title": "UPSC Mains GS Paper I — Indian Heritage, History & Geography 2021",
                        "language": "English",
                        "has_answer_key": False,
                        "file_size": 4123456,
                    },
                    {
                        "year": 2022,
                        "title": "UPSC Mains GS Paper I 2022",
                        "language": "English",
                        "has_answer_key": False,
                        "file_size": 4234567,
                    },
                    {
                        "year": 2023,
                        "title": "UPSC Mains GS Paper I 2023",
                        "language": "English",
                        "has_answer_key": False,
                        "file_size": 4312345,
                    },
                ],
            },
        ],
    },

    # ── JEE ─────────────────────────────────────────────────────────────────
    {
        "name": "JEE",
        "slug": "jee",
        "description": (
            "Joint Entrance Examination is India's premier engineering entrance test "
            "for admission to IITs, NITs, and other centrally funded institutions. "
            "Conducted in two stages: JEE Main and JEE Advanced."
        ),
        "accent_color_hex": "#2E5FA3",
        "categories": [
            {
                "name": "JEE Main — Session 1",
                "slug": "jee-main-session-1",
                "subjects": ["Physics", "Chemistry", "Mathematics"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "JEE Main 2019 January — Paper 1 (B.E./B.Tech)",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2345678,
                    },
                    {
                        "year": 2020,
                        "title": "JEE Main 2020 January — Paper 1 (B.E./B.Tech)",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2456789,
                    },
                    {
                        "year": 2021,
                        "title": "JEE Main 2021 February Session — Paper 1",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2567890,
                    },
                    {
                        "year": 2022,
                        "title": "JEE Main 2022 June Session — Paper 1",
                        "language": "English/Hindi/Gujarati",
                        "has_answer_key": True,
                        "file_size": 2678901,
                    },
                    {
                        "year": 2023,
                        "title": "JEE Main 2023 January Session — Paper 1",
                        "language": "English/Hindi/Gujarati",
                        "has_answer_key": True,
                        "file_size": 2789012,
                    },
                ],
            },
            {
                "name": "JEE Main — Session 2",
                "slug": "jee-main-session-2",
                "subjects": ["Physics", "Chemistry", "Mathematics"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "JEE Main 2019 April — Paper 1 (B.E./B.Tech)",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2312345,
                    },
                    {
                        "year": 2021,
                        "title": "JEE Main 2021 March Session — Paper 1",
                        "language": "English/Hindi",
                        "has_answer_key": True,
                        "file_size": 2423456,
                    },
                    {
                        "year": 2022,
                        "title": "JEE Main 2022 July Session — Paper 1",
                        "language": "English/Hindi/Gujarati",
                        "has_answer_key": True,
                        "file_size": 2534567,
                    },
                    {
                        "year": 2023,
                        "title": "JEE Main 2023 April Session — Paper 1",
                        "language": "English/Hindi/Gujarati",
                        "has_answer_key": True,
                        "file_size": 2645678,
                    },
                ],
            },
            {
                "name": "JEE Advanced",
                "slug": "jee-advanced",
                "subjects": ["Physics", "Chemistry", "Mathematics"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "JEE Advanced 2019 — Paper 1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3234567,
                    },
                    {
                        "year": 2019,
                        "title": "JEE Advanced 2019 — Paper 2",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3145678,
                    },
                    {
                        "year": 2021,
                        "title": "JEE Advanced 2021 — Paper 1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3456789,
                    },
                    {
                        "year": 2022,
                        "title": "JEE Advanced 2022 — Paper 1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3567890,
                    },
                    {
                        "year": 2023,
                        "title": "JEE Advanced 2023 — Paper 1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3678901,
                    },
                    {
                        "year": 2023,
                        "title": "JEE Advanced 2023 — Paper 2",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3589012,
                    },
                ],
            },
        ],
    },

    # ── NEET ────────────────────────────────────────────────────────────────
    {
        "name": "NEET",
        "slug": "neet",
        "description": (
            "National Eligibility cum Entrance Test is India's single medical entrance "
            "exam for admission to MBBS, BDS, Ayush, and other medical programs across "
            "all medical colleges in India."
        ),
        "accent_color_hex": "#7A4FA0",
        "categories": [
            {
                "name": "NEET UG",
                "slug": "neet-ug",
                "subjects": ["Physics", "Chemistry", "Biology (Botany & Zoology)"],
                "papers": [
                    {
                        "year": 2019,
                        "title": "NEET UG 2019 — Code P1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3123456,
                    },
                    {
                        "year": 2019,
                        "title": "NEET UG 2019 — Tamil Medium",
                        "language": "Tamil",
                        "has_answer_key": True,
                        "file_size": 3234567,
                    },
                    {
                        "year": 2020,
                        "title": "NEET UG 2020 — Code E1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3345678,
                    },
                    {
                        "year": 2021,
                        "title": "NEET UG 2021 — Code M6",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3456789,
                    },
                    {
                        "year": 2021,
                        "title": "NEET UG 2021 — Tamil Medium",
                        "language": "Tamil",
                        "has_answer_key": True,
                        "file_size": 3512345,
                    },
                    {
                        "year": 2022,
                        "title": "NEET UG 2022 — Code R1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3567890,
                    },
                    {
                        "year": 2023,
                        "title": "NEET UG 2023 — Code Z1",
                        "language": "English",
                        "has_answer_key": True,
                        "file_size": 3678901,
                    },
                    {
                        "year": 2023,
                        "title": "NEET UG 2023 — Tamil Medium",
                        "language": "Tamil",
                        "has_answer_key": True,
                        "file_size": 3745678,
                    },
                ],
            },
            {
                "name": "NEET PG",
                "slug": "neet-pg",
                "subjects": ["Clinical Medicine", "Para-Clinical Sciences", "Pre-Clinical Sciences"],
                "papers": [
                    {
                        "year": 2020,
                        "title": "NEET PG 2020 — National Board of Examinations",
                        "language": "English",
                        "has_answer_key": False,
                        "file_size": 4123456,
                    },
                    {
                        "year": 2021,
                        "title": "NEET PG 2021",
                        "language": "English",
                        "has_answer_key": False,
                        "file_size": 4234567,
                    },
                    {
                        "year": 2022,
                        "title": "NEET PG 2022",
                        "language": "English",
                        "has_answer_key": False,
                        "file_size": 4345678,
                    },
                    {
                        "year": 2023,
                        "title": "NEET PG 2023",
                        "language": "English",
                        "has_answer_key": False,
                        "file_size": 4456789,
                    },
                ],
            },
        ],
    },
]


def get_or_create_subject(name: str) -> Subject:
    subject = Subject.query.filter_by(name=name).first()
    if not subject:
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.flush()
    return subject


def seed():
    print("🌱  Starting ExamVault seed script...")

    # ── Create admin user ────────────────────────────────────────────────────
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@examvault.in")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@1234")

    if not User.query.filter_by(email=admin_email).first():
        admin = User(name="Admin", email=admin_email, role="admin")
        admin.set_password(admin_password)
        db.session.add(admin)
        print(f"  ✓ Admin user created: {admin_email}")
    else:
        print(f"  · Admin user already exists: {admin_email}")

    db.session.flush()
    
    sample_pdf_url = ensure_sample_pdf()

    # ── Seed exams ───────────────────────────────────────────────────────────
    total_papers = 0
    for exam_data in SEED_DATA:
        exam = Exam.query.filter_by(slug=exam_data["slug"]).first()
        if not exam:
            exam = Exam(
                name=exam_data["name"],
                slug=exam_data["slug"],
                description=exam_data["description"],
                accent_color_hex=exam_data["accent_color_hex"],
            )
            db.session.add(exam)
            db.session.flush()
            print(f"  ✓ Exam created: {exam.name}")
        else:
            print(f"  · Exam already exists: {exam.name}")

        for cat_data in exam_data["categories"]:
            category = ExamCategory.query.filter_by(
                exam_id=exam.id, slug=cat_data["slug"]
            ).first()
            if not category:
                category = ExamCategory(
                    exam_id=exam.id,
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                )
                db.session.add(category)
                db.session.flush()
                print(f"    ✓ Category: {category.name}")
            else:
                print(f"    · Category already exists: {category.name}")

            subjects = [get_or_create_subject(s) for s in cat_data.get("subjects", [])]

            for paper_data in cat_data["papers"]:
                existing = Paper.query.filter_by(
                    exam_category_id=category.id,
                    year=paper_data["year"],
                    title=paper_data["title"],
                ).first()
                if not existing:
                    paper = Paper(
                        exam_category_id=category.id,
                        year=paper_data["year"],
                        title=paper_data["title"],
                        language=paper_data["language"],
                        pdf_url=sample_pdf_url,
                        file_size=paper_data.get("file_size"),
                        has_answer_key=paper_data.get("has_answer_key", False),
                        answer_key_pdf_url=sample_pdf_url if paper_data.get("has_answer_key", False) else None,
                        download_count=0,
                    )
                    paper.subjects.extend(subjects)
                    db.session.add(paper)
                    total_papers += 1

    db.session.commit()

    paper_count = Paper.query.count()
    exam_count = Exam.query.count()
    print(f"\n✅  Seed complete!")
    print(f"   Exams: {exam_count}")
    print(f"   Total papers in DB: {paper_count}")
    print(f"   Papers added this run: {total_papers}")
    print(f"\n   Admin login: {admin_email} / {admin_password}")


if __name__ == "__main__":
    app = create_app("development")
    with app.app_context():
        seed()
