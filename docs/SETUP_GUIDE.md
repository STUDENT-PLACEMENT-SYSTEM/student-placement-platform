# 🚀 Developer Setup & Deployment Guide

This guide walks you through setting up the local development environment using Docker Compose, configuring environment variables, running migrations, and seeding the database with 3,000 synthetic Indian engineering students.

---

## 1. Prerequisites

Ensure the following tools are installed on your machine:
- **Docker & Docker Compose:** Docker Desktop or Docker Engine v24+
- **Python 3.11+**
- **Node.js 18+ (LTS) & npm / pnpm**
- **Git**

---

## 2. Environment Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Key Environment Variables (`.env`)
```ini
# Application
ENVIRONMENT=development
PROJECT_NAME="Student Placement Analytics Platform"
SECRET_KEY=change-me-to-a-secure-random-32-byte-hex-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (PostgreSQL 16 + pgvector)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=placement_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Redis (Pub/Sub & Caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

# MinIO / S3 Object Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET_RESUMES=placement-resumes
MINIO_BUCKET_JDS=placement-jds
MINIO_BUCKET_OFFERS=placement-offers
MINIO_USE_SSL=false

# LLM & Embeddings (Optional for offline mock mode)
OPENAI_API_KEY=mock-key-or-real-openai-key
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

---

## 3. Starting Infrastructure Services

Run PostgreSQL (`pgvector`), Redis, and MinIO in the background:
```bash
docker compose up -d postgres redis minio
```

Verify all three containers are healthy:
```bash
docker compose ps
```

- **PostgreSQL:** Running on `localhost:5432`
- **Redis:** Running on `localhost:6379`
- **MinIO S3 API:** Running on `localhost:9000`
- **MinIO Web Console:** Open [http://localhost:9001](http://localhost:9001) in your browser (`minioadmin` / `minioadmin`)

---

## 4. Database Migrations

With Postgres running, initialize tables using Alembic:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

alembic upgrade head
```

---

## 5. Generating & Seeding 3,000 Synthetic Students

Run the synthetic data generation and database seeder:
```bash
cd ../scripts
python generate_synthetic_3000.py
python seed_database.py
```
This script populates:
- 3,000 student accounts across CS, IT, ECE, EE, ME, Civil branches with realistic Indian GPAs, backlogs, technical skill sets, and historical placement records.
- 50+ placement drives from top recruiters (Google, Microsoft, TCS, Infosys, Amazon, Larsen & Toubro, etc.).
- Default Admin & TPO credentials for immediate login.

---

## 6. Running Application Services

### Running FastAPI Backend:
```bash
cd ../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger Documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Running Background Worker:
```bash
cd ../worker
python worker_main.py
```

### Running FastMCP Server:
```bash
cd ../mcp_server
python server.py
```

### Running Next.js Frontend:
```bash
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to access the web application.
