# ExamVault 🗂️

> **The Archive Cabinet** — Previous Year Question Papers for TNPSC, UPSC, JEE, and NEET

A full-stack PWA platform organised by exam → category → year → paper.

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (default) or MySQL 8

### 1 — Backend

```powershell
cd backend

# First run only:
Copy-Item .env.example .env   # edit if you want MySQL
.\setup.ps1                   # installs deps, migrates DB, seeds data

# Every run:
flask run
# → http://localhost:5000/health
```

### 2 — Frontend

```powershell
cd frontend
.\setup.ps1      # installs npm packages
npm run dev
# → http://localhost:5173
```

## Architecture

```
exam/
├── backend/         Flask + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── models/      Exam, Paper, User, Bookmark
│   │   ├── blueprints/  auth, exams, papers, bookmarks, admin
│   │   └── utils/       JWT helpers, PDF validators
│   ├── seeds/       Seed data for all 4 exams
│   └── README.md    Full API documentation
└── frontend/        React 18 + Vite + Zustand
    └── src/
        ├── api/         Axios client
        ├── pages/       Home, Exam, Year, PaperDetail, Search, Auth, Bookmarks
        ├── components/  Navbar, Badges, Skeleton, Toast
        ├── hooks/       useDebounce
        └── store/       Zustand (auth + toasts)
```

## Exam Coverage

| Exam  | Accent Color | Categories                                      |
|-------|-------------|--------------------------------------------------|
| TNPSC | `#C1483A`   | Group 1, Group 2, Group 4, VAO                   |
| UPSC  | `#1F6F5C`   | Prelims GS-I, Prelims CSAT, Mains GS-I           |
| JEE   | `#2E5FA3`   | JEE Main Session 1 & 2, JEE Advanced             |
| NEET  | `#7A4FA0`   | NEET UG, NEET PG                                 |

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ | Database schema + backend foundation |
| 2 | ✅ | All API endpoints |
| 3 | ✅ | Frontend core browsing (no animation) |
| 4 | ⬜ | 3D UI + Framer Motion + GSAP |
| 5 | ⬜ | PWA + Offline support |
| 6 | ⬜ | SEO + Sitemap + Admin dashboard |

See [backend/README.md](./backend/README.md) for full API documentation.
