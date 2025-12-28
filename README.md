# TaskFlow — AI-Assisted Productivity & Planning

TaskFlow is a modern, cloud-ready task manager with an AI assistant that helps you prioritize tasks, generate a daily plan, and keep momentum. Built as a real-world, production-style project to showcase backend + AI + cloud skills.

## Quick Start (Docker)

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

Then open:
- **Backend API docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

## Features

- **Task Management**: Projects, tasks, due dates, statuses, tags
- **AI Assistant**: OpenAI-powered prioritization with rationale and daily plan generation
- **Search & Filters**: By project, status, tags, due range
- **Auth**: Register/login with JWT tokens
- **Fast APIs**: FastAPI + Pydantic + OpenAPI docs
- **Scalable DB**: PostgreSQL + SQLAlchemy + Alembic migrations
- **Caching & Rate Limiting**: Redis-backed with per-user limits
- **DevOps Ready**: Docker, CI/CD (GitHub Actions), Prometheus metrics, AWS ECS deployment

## Architecture

```
┌─────────────────────────────┐
│  React (Vite + Tailwind)    │
└──────────────┬──────────────┘
               │ HTTPS (JWT)
┌──────────────▼──────────────┐
│  FastAPI Backend            │
│  - /auth, /tasks, /projects │
│  - /ai/prioritize, /metrics │
└──────────────┬──────────────┘
               │
     ┌─────────┼──────────┐
     │         │          │
┌────▼─┐  ┌───▼──┐  ┌────▼────────┐
│Redis │  │  PG  │  │ OpenAI API   │
│cache │  │  DB  │  │ (external)   │
└──────┘  └──────┘  └─────────────┘
```

## Tech Stack

- **Frontend**: React (Vite), Tailwind, React Query
- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, JWT
- **Databases**: PostgreSQL, Redis
- **AI**: OpenAI GPT-4, rule-based fallback
- **DevOps**: Docker, Docker Compose, GitHub Actions, AWS ECS + RDS + ECR
- **Testing**: pytest, httpx, React Testing Library

## Repository Structure

```
taskflow/
├── backend/
│   ├── app/
│   │   ├── main.py              (FastAPI app and routes)
│   │   ├── config.py            (settings via pydantic)
│   │   ├── models.py            (SQLAlchemy models)
│   │   ├── schemas.py           (Pydantic DTOs)
│   │   ├── deps.py              (dependencies: db, auth)
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   ├── projects.py
│   │   │   └── ai.py
│   │   ├── services/
│   │   │   ├── ai.py            (rule-based + LLM adapter)
│   │   │   └── tasks.py         (business logic)
│   │   └── utils/               (hashing, rate limit, logging)
│   ├── alembic/                 (DB migrations)
│   ├── tests/                   (pytest)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Environment Variables (.env)

### Backend

```
DATABASE_URL=postgresql+psycopg://taskflow:taskflow@db:5432/taskflow
REDIS_URL=redis://cache:6379/0
JWT_SECRET=your_super_secret_key_change_this
OPENAI_API_KEY=sk-your_openai_key_here
AI_PROVIDER=openai
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

### Frontend

```
VITE_API_BASE=http://localhost:8000
```

## Running Locally

### With Docker (recommended)

```bash
# Build and start all services
docker compose up -d --build

# Run migrations
docker compose exec api alembic upgrade head

# Check logs
docker compose logs -f api

# Stop
docker compose down
```

### Without Docker

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Auth

- `POST /auth/register` — email, password → access_token, refresh_token
- `POST /auth/login` — email, password → access_token, refresh_token
- `POST /auth/refresh` — refresh_token → access_token

### Tasks

- `GET /tasks?status=&project_id=&due_from=&due_to=&skip=0&limit=20` — list tasks
- `POST /tasks` — create task
- `GET /tasks/{id}` — get task
- `PATCH /tasks/{id}` — update task
- `DELETE /tasks/{id}` — delete task

### Projects

- `GET /projects` — list projects
- `POST /projects` — create project
- `PATCH /projects/{id}` — update project
- `DELETE /projects/{id}` — delete project

### AI

- `POST /ai/prioritize` — prioritize a list of tasks with OpenAI

Example request:

```json
{
  "tasks": [
    {
      "title": "Finish OS HW2",
      "due_at": "2025-02-01T17:00:00Z",
      "estimated_minutes": 120,
      "importance": 5
    },
    {
      "title": "Apply to 5 SWE internships",
      "due_at": null,
      "estimated_minutes": 90,
      "importance": 4
    }
  ]
}
```

Example response:

```json
{
  "results": [
    {
      "title": "Finish OS HW2",
      "score": 0.91,
      "rationale": "Imminent deadline; high importance; manageable effort."
    },
    {
      "title": "Apply to 5 SWE internships",
      "score": 0.78,
      "rationale": "Career critical; no hard deadline; schedule today if time remains."
    }
  ],
  "plan": [
    "14:00-16:00 Finish OS HW2",
    "16:15-17:45 Apply to internships",
    "18:00-19:00 Break and review progress"
  ]
}
```

### Health & Observability

- `GET /healthz` — health check
- `GET /readyz` — readiness check
- `GET /metrics` — Prometheus metrics

## Testing

### Backend

```bash
docker compose exec api pytest -v
```

### Frontend

```bash
cd frontend
npm test
```

## Deployment

### AWS ECS + RDS + ECR

1. Build and push images to ECR:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t taskflow-api backend/
docker tag taskflow-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/taskflow-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/taskflow-api:latest
```

2. Create ECS task definition, service, load balancer (see Terraform in `/infra` or AWS Console)

3. Create RDS Postgres and ElastiCache Redis in same VPC

4. Set environment variables in ECS task definition

### Simpler Alternative: Render or Railway

- Push repo to GitHub
- Connect to Render/Railway
- Add Postgres and Redis add-ons
- Set environment variables
- Deploy

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

- Run pytest and frontend tests on every PR
- Build Docker images
- Push to ECR on main branch
- Deploy to ECS on tag

## Performance & Cost

- **Cold start**: ~2s (FastAPI startup)
- **Median latency** (GET /tasks): ~45ms (local, with cache)
- **Monthly cost** (AWS ECS + RDS + ECR): ~$50–100 depending on instance sizing

