# ExamVault API Reference

All endpoints are prefixed with `http://localhost:5000` in development.
The Vite dev server proxies `/api/*` → `http://localhost:5000/*`.

---

## Authentication

### POST /auth/register
Create a new user account.

**Request:**
```json
{ "name": "Arjun Kumar", "email": "arjun@example.com", "password": "secret123" }
```
**Response 201:**
```json
{
  "message": "Account created successfully",
  "access_token": "eyJ...",
  "user": { "id": 1, "name": "Arjun Kumar", "email": "arjun@example.com", "role": "user" }
}
```

---

### POST /auth/login
Login and receive a JWT.

**Request:**
```json
{ "email": "arjun@example.com", "password": "secret123" }
```
**Response 200:**
```json
{ "access_token": "eyJ...", "user": { ... } }
```

---

### GET /auth/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{ "user": { "id": 1, "name": "Arjun Kumar", "role": "user", ... } }
```

---

## Exams

### GET /exams/
List all 4 exams.

**Response 200:**
```json
{
  "exams": [
    { "id": 1, "name": "TNPSC", "slug": "tnpsc", "description": "...", "accent_color_hex": "#C1483A" },
    { "id": 2, "name": "UPSC",  "slug": "upsc",  "description": "...", "accent_color_hex": "#1F6F5C" },
    { "id": 3, "name": "JEE",   "slug": "jee",   "description": "...", "accent_color_hex": "#2E5FA3" },
    { "id": 4, "name": "NEET",  "slug": "neet",  "description": "...", "accent_color_hex": "#7A4FA0" }
  ]
}
```

---

### GET /exams/{slug}
Single exam with all categories.

**Example:** `GET /exams/tnpsc`

**Response 200:**
```json
{
  "exam": {
    "id": 1, "name": "TNPSC", "slug": "tnpsc", "accent_color_hex": "#C1483A",
    "categories": [
      { "id": 1, "exam_id": 1, "name": "Group 1", "slug": "group-1" },
      { "id": 2, "exam_id": 1, "name": "Group 2", "slug": "group-2" }
    ]
  }
}
```

---

### GET /exams/{slug}/categories
Categories for a given exam.

**Example:** `GET /exams/upsc/categories`

**Response 200:**
```json
{
  "exam_slug": "upsc",
  "categories": [
    { "id": 5, "name": "Prelims — GS Paper I", "slug": "prelims-gs-1" },
    { "id": 6, "name": "Prelims — CSAT Paper II", "slug": "prelims-csat" }
  ]
}
```

---

### GET /exams/{slug}/years
Distinct years with papers, newest first.

**Query params:** `category=<slug>` (optional)

**Example:** `GET /exams/jee/years?category=jee-advanced`

**Response 200:**
```json
{ "exam_slug": "jee", "years": [2023, 2022, 2021, 2019] }
```

---

## Papers

### GET /papers/
Filtered, paginated paper list.

**Query params:**
| Param      | Example             | Description                |
|------------|---------------------|----------------------------|
| exam       | `tnpsc`             | Exam slug                  |
| category   | `group-1`           | Category slug              |
| year       | `2023`              | Paper year                 |
| subject    | `Physics`           | Subject name (partial)     |
| search     | `group 4`           | Title keyword search       |
| language   | `Tamil`             | Language filter            |
| page       | `1`                 | Page number                |
| per_page   | `20`                | Results per page (max 100) |

**Example:** `GET /papers/?exam=neet&year=2023&language=Tamil`

**Response 200:**
```json
{
  "papers": [
    {
      "id": 42, "year": 2023, "title": "NEET UG 2023 — Tamil Medium",
      "language": "Tamil", "has_answer_key": true,
      "download_count": 1240, "file_size": 3745678,
      "subjects": [{ "id": 1, "name": "Physics" }, ...],
      "category": { "id": 9, "name": "NEET UG", "slug": "neet-ug" },
      "exam": { "id": 4, "name": "NEET", "slug": "neet", "accent_color_hex": "#7A4FA0" }
    }
  ],
  "pagination": { "page": 1, "per_page": 20, "total": 1, "pages": 1 }
}
```

---

### GET /papers/{id}
Single paper detail.

**Example:** `GET /papers/1`

**Response 200:** `{ "paper": { ... full paper object ... } }`

---

### GET /papers/{id}/download
Increment download count and get PDF URL.

**Example:** `GET /papers/1/download`

**Response 200:**
```json
{
  "paper_id": 1,
  "pdf_url": "/uploads/abc123.pdf",
  "title": "TNPSC Group 1 Preliminary Examination 2023",
  "download_count": 4321
}
```

---

## Bookmarks (JWT required)

All bookmark routes require `Authorization: Bearer <token>` header.

### GET /bookmarks/
List user's bookmarks with full paper data.

### POST /bookmarks/
Add a bookmark.
```json
{ "paper_id": 42 }
```

### DELETE /bookmarks/{id}
Remove a bookmark by bookmark ID.

### DELETE /bookmarks/paper/{paper_id}
Remove a bookmark by paper ID (convenience endpoint).

---

## Admin (JWT + admin role required)

### POST /admin/papers
Upload a new paper. Uses `multipart/form-data`.

**Fields:**
| Field           | Required | Description                        |
|-----------------|----------|------------------------------------|
| file            | ✓        | PDF file (max 50 MB)               |
| title           | ✓        | Paper title                        |
| exam_category_id| ✓        | ID from exam_categories table      |
| year            | ✓        | 4-digit year (1990–2030)           |
| language        |          | Default: "English"                 |
| subjects        |          | Comma-separated subject names      |
| answer_key      |          | Optional answer key PDF            |

**Validations:**
- File must have `.pdf` extension
- File magic bytes must be `%PDF-`
- Max file size: 50 MB

**Response 201:** `{ "message": "...", "paper": { ... } }`

**Errors:**
- `400` — Missing required field or invalid file
- `403` — Not an admin
- `404` — exam_category_id not found

---

### GET /admin/stats
Per-exam statistics.

**Response 200:**
```json
{
  "stats": [
    { "exam": "JEE",  "slug": "jee",  "paper_count": 15, "total_downloads": 42500 },
    { "exam": "NEET", "slug": "neet", "paper_count": 12, "total_downloads": 38200 },
    { "exam": "TNPSC","slug": "tnpsc","paper_count": 18, "total_downloads": 67100 },
    { "exam": "UPSC", "slug": "upsc", "paper_count": 13, "total_downloads": 51800 }
  ]
}
```

---

## Health Check

### GET /health
```json
{ "status": "ok", "app": "ExamVault API" }
```
