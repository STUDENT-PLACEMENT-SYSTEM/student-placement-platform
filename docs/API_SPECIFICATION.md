# 📡 API Specification & Real-Time Event Contracts

**Base URL:** `http://localhost:8000/api/v1`  
**Authentication Scheme:** Bearer Token (JWT in `Authorization: Bearer <token>`)

---

## 1. Authentication & RBAC Rules Matrix

| Role | Permitted Route Prefixes |
|---|---|
| **Student** | `/auth/*`, `/students/*`, `/drives` (view eligible & apply) |
| **Recruiter** | `/auth/*`, `/recruiters/*`, `/drives/*` (own drives only) |
| **TPO (Placement Officer)** | `/auth/*`, `/tpo/*`, `/drives/*`, `/analytics/*`, `/students` (read-only) |
| **Super Admin** | Full access to all endpoints + `/admin/*` |

---

## 2. Authentication Endpoints (`/auth`)

### `POST /auth/register`
Creates a new account (Student or Recruiter).
- **Request Body:**
```json
{
  "email": "student@college.edu",
  "password": "SecurePassword123!",
  "role": "student",
  "full_name": "Rohan Sharma",
  "roll_number": "2021CS045",
  "branch": "Computer Science",
  "batch_year": 2025
}
```
- **Response (201 Created):**
```json
{
  "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "email": "student@college.edu",
  "role": "student",
  "is_active": true,
  "message": "Account registered successfully"
}
```

### `POST /auth/login`
Authenticates user and returns JWT token pair.
- **Request Body (OAuth2 Form / JSON):**
```json
{
  "email": "student@college.edu",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "refresh_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "expires_in": 3600,
  "role": "student",
  "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

---

## 3. Student Endpoints (`/students`)

### `POST /students/resume/upload`
Uploads resume PDF to MinIO and enqueues an asynchronous parsing job.
- **Headers:** `Authorization: Bearer <student_token>`, `Content-Type: multipart/form-data`
- **Form Data:** `file`: `resume.pdf`
- **Response (202 Accepted):**
```json
{
  "status": "queued",
  "task_id": "arq:task:b9a8cf12",
  "s3_key": "resumes/2021CS045/resume_v1.pdf",
  "message": "Resume uploaded successfully. Parsing running in background."
}
```

### `GET /students/placement-prediction`
Returns real-time XGBoost ML placement probability and expected CTC range for the authenticated student.
- **Response (200 OK):**
```json
{
  "student_id": "45d12a67-...",
  "placement_probability": 87.5,
  "placement_tier": "High Chance",
  "predicted_ctc_range": {
    "min_lpa": 8.0,
    "median_lpa": 12.5,
    "max_lpa": 16.0
  },
  "top_influencing_factors": [
    {"feature": "CGPA", "weight": 0.35, "status": "Positive (8.62)"},
    {"feature": "Internships", "weight": 0.28, "status": "Positive (2)"},
    {"feature": "Backlogs", "weight": -0.05, "status": "Clear (0)"}
  ]
}
```

### `POST /students/skill-gap-roadmap`
Invokes the LangGraph RAG Agent to construct a 4-week tailored preparation plan.
- **Request Body:**
```json
{
  "target_drive_id": "8e3b1c2a-..."
}
```
- **Response (200 OK):**
```json
{
  "target_role": "Backend Software Engineer",
  "target_company": "Amazon",
  "readiness_score": 72.0,
  "missing_skills": ["Kafka", "System Design", "Distributed Caching"],
  "weekly_roadmap": [
    {
      "week": 1,
      "focus": "Advanced Concurrency & Redis Caching",
      "action_items": [
        "Implement rate limiter in FastAPI using Redis",
        "Practice 10 Hard Graph questions on LeetCode"
      ],
      "recommended_resources": ["https://redis.io/docs/manual/patterns/"]
    }
  ]
}
```

---

## 4. Recruiter Endpoints (`/recruiters`)

### `POST /recruiters/drives`
Create a new placement drive requirement.
- **Request Body:**
```json
{
  "title": "Software Development Engineer - 1",
  "role_name": "SDE-1",
  "job_description": "We are seeking a strong backend engineer experienced in Python, Docker, and PostgreSQL...",
  "min_cgpa": 7.50,
  "max_backlogs": 0,
  "allowed_branches": ["Computer Science", "Information Technology", "ECE"],
  "ctc_min_lpa": 10.0,
  "ctc_max_lpa": 14.0,
  "job_location": "Bangalore / Hybrid",
  "drive_date": "2026-12-15",
  "registration_deadline": "2026-12-05T23:59:59Z"
}
```

### `POST /recruiters/drives/{drive_id}/semantic-search`
Runs a pgvector semantic search over all students who applied to this drive.
- **Request Body:**
```json
{
  "query": "Students with experience in Kubernetes, microservices, and high concurrency",
  "top_k": 10
}
```
- **Response (200 OK):**
```json
{
  "matches": [
    {
      "student_id": "45d12a67-...",
      "roll_number": "2021CS045",
      "full_name": "Rohan Sharma",
      "similarity_score": 0.912,
      "matched_skills": ["Docker", "Kubernetes", "FastAPI"],
      "cgpa": 8.62
    }
  ]
}
```

---

## 5. TPO & Real-Time Analytics Endpoints (`/tpo` & `/analytics`)

### `POST /tpo/offers/mark-placed`
Marks a student as placed, commits to DB, updates Redis KPI cache, and publishes real-time event.
- **Request Body:**
```json
{
  "student_id": "45d12a67-...",
  "drive_id": "8e3b1c2a-...",
  "company_name": "Google",
  "ctc_lpa": 28.5,
  "is_on_campus": true
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "offer_id": "d1c2b3a4-...",
  "message": "Student Rohan Sharma marked as placed at Google (28.5 LPA)."
}
```

### `GET /analytics/live-kpis` (SSE Stream)
- **Protocol:** Server-Sent Events (`text/event-stream`)
- **Headers:** `Authorization: Bearer <tpo_token>`
- **Live Event Payload:**
```text
event: kpi_update
data: {
  "timestamp": "2026-11-24T09:15:00Z",
  "total_students": 3000,
  "placed_students": 1945,
  "placement_percentage": 64.83,
  "average_ctc_lpa": 9.24,
  "median_ctc_lpa": 7.50,
  "highest_ctc_lpa": 44.00,
  "total_offers": 2310,
  "branch_breakdown": {
    "Computer Science": {"placed": 580, "total": 600, "percent": 96.6},
    "Information Technology": {"placed": 380, "total": 400, "percent": 95.0},
    "ECE": {"placed": 410, "total": 500, "percent": 82.0}
  },
  "recent_offer": {
    "student_name": "Rohan Sharma",
    "company": "Google",
    "ctc_lpa": 28.5
  }
}
```
