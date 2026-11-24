# 🏛️ System Architecture Design Document

**Project:** Student Placement Analytics & Career Intelligence Platform  
**Architecture Style:** Modular Monolith + Asynchronous AI Worker  
**Target Scale:** Single University / College (~3,000 active students, ~200 placement drives/year)

---

## 1. Architectural Philosophy & Strategy

Modern enterprise software often falls into the trap of premature microservices: distributed transactions, network latency, complex observability overhead, and high deployment costs. For an academic institution of ~3,000 students:
1. **Core API is a Modular Monolith:** A single FastAPI deployment with strictly bounded domain contexts (`auth`, `students`, `recruiters`, `tpo`, `drives`, `analytics`, `ml`). Each domain owns its models, schemas, services, and routers.
2. **Heavy Computing is Offloaded to an Asynchronous Worker:** Heavy operations (extracting text from complex multi-page PDF resumes, running LLM structured extraction, generating 1536-dimensional embeddings, and bulk CSV ingestion) run on an independent worker (ARQ / Celery) backed by Redis.
3. **Database Unification with `pgvector`:** Instead of maintaining a separate vector database (e.g., Pinecone/Milvus) alongside a relational database, PostgreSQL 16 with the `pgvector` extension serves both relational and vector data in a single transactional engine.
4. **Decoupled Event-Driven Bus via Redis Pub/Sub:** Real-time metrics and notifications communicate through internal domain events, ensuring loose coupling between modules.

---

## 2. High-Level System Architecture Diagram

```mermaid
flowchart TB
    subgraph ClientLayer["Frontend Application Layer (Next.js 14)"]
        direction TB
        SP["Student Portal (App Router)"]
        RP["Recruiter Portal (App Router)"]
        TP["TPO Command Center (App Router)"]
        AP["Super Admin Console (App Router)"]
    end

    subgraph APILayer["FastAPI Modular Monolith (Core API)"]
        direction TB
        Router["FastAPI Ingress Router & CORS"]
        SecurityMW["JWT Security Middleware & RBAC Dependency Guard"]
        
        subgraph Domains["Isolated Domain Modules"]
            D_Auth["Auth Module\n(Login, Register, Refresh)"]
            D_Student["Student Module\n(Profile, Resume Upload)"]
            D_Recruiter["Recruiter Module\n(JD Creation, Candidate Review)"]
            D_Drives["Drives Module\n(Applications, Status Tracking)"]
            D_TPO["TPO Module\n(Drive Approval, Mark Placed, Ingestion)"]
            D_Analytics["Analytics Module\n(Redis KPI Aggregator & SSE)"]
            D_ML["ML Inference Module\n(Placement & CTC Predictor)"]
        end
    end

    subgraph AsyncWorkerLayer["Asynchronous AI Worker (ARQ / Celery)"]
        direction TB
        WorkerConsumer["Task Consumer (Redis Queue)"]
        LangGraphResume["LangGraph Resume Parsing Engine"]
        LangGraphRoadmap["LangGraph RAG Skill-Gap Engine"]
        BatchImporter["Bulk 3,000 Student Ingestion Worker"]
    end

    subgraph FastMCPLayer["Model Context Protocol (FastMCP)"]
        direction TB
        MCPServer["FastMCP Read-Only Server"]
        BranchStats["get_branch_placement_stats"]
        EligibleTool["find_eligible_students"]
        UnplacedTool["get_unplaced_high_cgpa_students"]
        CompanyTool["get_company_offer_summary"]
    end

    subgraph StorageLayer["Data & Persistence Infrastructure"]
        Postgres[("PostgreSQL 16 + pgvector\nRelational Tables + HNSW Index")]
        RedisStore[("Redis 7.2\nTask Queue + Pub/Sub + KPI Cache")]
        MinIOStore[("MinIO (S3-compatible)\nResumes, JDs, Offer Letters")]
    end

    ClientLayer -->|REST HTTPS| Router
    ClientLayer -->|SSE Live Stream| D_Analytics
    Router --> SecurityMW
    SecurityMW --> Domains

    Domains -->|Read/Write ACID Queries| Postgres
    Domains -->|Cache Invalidation & Pub/Sub| RedisStore
    Domains -->|Presigned Uploads & Downloads| MinIOStore
    Domains -->|Enqueue Long-Running Tasks| RedisStore

    RedisStore -->|Poll Tasks| WorkerConsumer
    WorkerConsumer --> LangGraphResume & LangGraphRoadmap & BatchImporter
    LangGraphResume & LangGraphRoadmap -->|Write Vectors & Structured Data| Postgres

    TP -.->|Natural Language Query| MCPServer
    MCPServer --> BranchStats & EligibleTool & UnplacedTool & CompanyTool
    BranchStats & EligibleTool & UnplacedTool & CompanyTool -->|Read-Only Parameterized SQL| Postgres
```

---

## 3. Domain Modules & Internal Communication

Each domain inside `backend/app/modules/` follows a standardized layered pattern:
```text
module/
├── router.py       # FastAPI APIRouter exposing versioned HTTP endpoints
├── schemas.py      # Pydantic v2 validation models for Request and Response
├── service.py      # Business logic orchestration & external client calls
└── repository.py   # Pure database queries using Async SQLAlchemy 2.0
```

### Module Responsibilities:
1. **`auth`**: Handles password hashing (`bcrypt`), JWT token generation, refresh tokens, role resolution, and user status.
2. **`students`**: Personal profile data, academic records, resume S3 key linking, viewing placement status.
3. **`recruiters`**: Company information, job description (JD) postings, viewing shortlisted students for posted drives.
4. **`drives`**: Placement drives lifecycle (draft -> pending approval -> active -> completed), student application submission, eligibility verification.
5. **`tpo`**: Drive approvals, bulk student roster imports, marking student as placed with verified CTC.
6. **`analytics`**: Real-time KPI aggregation (Placement %, average CTC, branch-wise placements), caching metrics in Redis, streaming live updates via Server-Sent Events (SSE).
7. **`ml`**: Real-time inference using serialized XGBoost pipelines (`placement_classifier.joblib`, `ctc_regressor.joblib`).

---

## 4. Real-Time Data Flow: Server-Sent Events (SSE)

When a placement event occurs (e.g., a student gets an offer of 12 LPA from Microsoft):

```mermaid
sequenceDiagram
    autonumber
    actor TPO as TPO User
    participant API as FastAPI TPO Module
    participant DB as PostgreSQL 16
    participant Redis as Redis Pub/Sub & Cache
    participant SSE as FastAPI SSE Channel
    actor Dash as TPO Live Dashboard

    Dash->>SSE: Connects to GET /api/v1/analytics/live-kpis
    SSE-->>Dash: HTTP 200 (text/event-stream open)
    
    TPO->>API: POST /api/v1/tpo/offers/mark-placed (StudentID, Microsoft, 12 LPA)
    API->>DB: INSERT into placement_offers & UPDATE students.placement_status
    DB-->>API: Transaction Committed
    
    API->>Redis: Invalidate key 'kpi:college_summary'
    API->>Redis: PUBLISH event 'tpo:live_analytics' { type: 'STUDENT_PLACED', ... }
    API-->>TPO: HTTP 200 OK
    
    Redis-->>SSE: Receives published event payload
    SSE-->>Dash: data: {"type": "KPI_UPDATE", "placed_count": 1842, "avg_ctc": 8.4, "top_company": "Microsoft"}
    Note over Dash: Dashboard updates live charts with no page reload
```

---

## 5. Security & Isolation Architecture

1. **Defense in Depth:**
   - Transport encryption (TLS) on all external ingress.
   - JWT tokens containing `sub` (User UUID) and `role` (`student`, `recruiter`, `tpo`, `admin`).
   - Role verification occurs at the FastAPI route dependency level via `require_role(["tpo", "admin"])`.
2. **Data Isolation (Multi-Tenancy within Single College):**
   - Students can only view their own profile, prediction, and roadmap.
   - Recruiters can only access student profiles who actively applied to their drives.
   - Resumes stored in MinIO are private; the frontend receives time-limited (15-minute) presigned URLs.
3. **Audit Logging:**
   - Sensitive administrative operations (drive approvals, marking offers, bulk uploads) automatically generate an immutable record in `audit_logs`.

---

## 6. Scalability & Extensibility Roadmap

The system is designed with explicit hooks for future extensions:

| Future Extension | Integration Point | Architecture Impact |
|---|---|---|
| **Alumni Mentorship** | New module `modules/alumni/` | Add `alumni_profiles` table, reuse `pgvector` for skill-based mentor matching |
| **AI Mock Interview** | New module `modules/mock_interviews/` | Integrate WebRTC / Whisper speech-to-text in worker, store feedback in Postgres |
| **WhatsApp/Email Alerts** | Subscribe to Redis Event Bus | New consumer daemon reading from `tpo:live_analytics` and dispatching Twilio/SendGrid alerts |
| **Hackathon & Contest Tracker** | New module `modules/contests/` | LeetCode/Codeforces API scraping tasks in background worker |
