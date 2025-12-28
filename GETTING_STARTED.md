# TaskFlow - Getting Started Guide

This guide walks you through building and deploying TaskFlow from scratch.

## Prerequisites

- Docker & Docker Compose installed
- Python 3.11+
- Node.js 18+
- Git
- OpenAI API key (optional, for AI features)

## Quick Start (5 minutes)

### 1. Clone and Setup

```bash
cd taskflow
cp .env.example .env
```

Update `.env` with your OpenAI API key (optional):
```
OPENAI_API_KEY=sk-your_key_here
```

### 2. Start Services

```bash
make up
```

Or manually:
```bash
docker compose up -d --build
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI Backend (port 8000)
- React Frontend (port 5173)

### 3. Access the App

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz

## First Test Flow

### 1. Create an Account

Go to http://localhost:5173 and register with an email and password (min 8 chars).

### 2. Test the API Directly

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'

# Save the access_token from response, then:

export TOKEN="your_access_token_here"

# Create a project
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My First Project","description":"Testing TaskFlow"}'

# Get projects (save project_id)
curl -X GET http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN"

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Finish OS HW2",
    "project_id":1,
    "status":"todo",
    "due_at":"2025-02-01T17:00:00Z",
    "estimated_minutes":120,
    "priority":5,
    "importance":5
  }'

# List tasks
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Test AI prioritization
curl -X POST http://localhost:8000/ai/prioritize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "title":"Finish OS HW2",
        "due_at":"2025-02-01T17:00:00Z",
        "estimated_minutes":120,
        "importance":5
      },
      {
        "title":"Apply to internships",
        "estimated_minutes":90,
        "importance":4
      }
    ]
  }'
```

## Development Workflow

### View Logs

```bash
make logs              # All services
make logs-api         # Just backend
make logs-db          # Just database
```

### Run Tests

```bash
make test             # Run pytest
make test-cov         # With coverage report
```

### Database Commands

```bash
make db-migrate       # Run migrations
make db-downgrade     # Rollback last migration
make db-shell         # Connect to PostgreSQL
redis-cli             # Connect to Redis
```

### Stop Services

```bash
make down             # Stop all services
make clean            # Stop and remove volumes (WARNING: deletes data)
```

## Project Structure

```
taskflow/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Settings
│   │   ├── models.py         # SQLAlchemy ORM
│   │   ├── schemas.py        # Pydantic DTOs
│   │   ├── deps.py           # Dependencies (DB, auth)
│   │   ├── routers/
│   │   │   ├── auth.py       # /auth endpoints
│   │   │   ├── tasks.py      # /tasks endpoints
│   │   │   ├── projects.py   # /projects endpoints
│   │   │   └── ai.py         # /ai endpoints
│   │   ├── services/
│   │   │   ├── ai.py         # AI logic (OpenAI + rule-based)
│   │   │   └── tasks.py      # Task business logic
│   │   └── utils/            # Utilities
│   ├── alembic/              # Database migrations
│   ├── tests/                # pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # React pages (Login, Register, Dashboard)
│   │   ├── components/       # Reusable components
│   │   ├── api/              # Axios client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env (local only)
├── .env.example
├── .gitignore
├── Makefile
├── README.md
└── LICENSE
```

## Next Steps

### Phase 1: Core Features (Current)
- ✅ Auth (register, login, JWT)
- ✅ CRUD for tasks and projects
- ✅ AI prioritization with OpenAI + rule-based fallback
- ✅ Prometheus metrics
- ✅ Docker setup

### Phase 2: Polish (Upcoming)
- [ ] Frontend task creation/editing UI
- [ ] Real-time AI updates
- [ ] Email notifications for due tasks
- [ ] Search and advanced filtering
- [ ] User preferences/settings

### Phase 3: Deployment
- [ ] AWS ECS setup (Terraform)
- [ ] ECR image registry
- [ ] RDS PostgreSQL
- [ ] ElastiCache Redis
- [ ] ALB + auto-scaling
- [ ] GitHub Actions auto-deploy on tag

## Troubleshooting

### Containers won't start

```bash
# Check logs
docker compose logs

# Rebuild everything
docker compose down -v
docker compose up -d --build
```

### Database migrations failed

```bash
# Manual migration
docker compose exec api alembic upgrade head

# Check migration status
docker compose exec api alembic current
```

### Port already in use

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Use 5433 instead
```

### OpenAI API errors

If `AI_PROVIDER=openai` but key is invalid, the system falls back to rule-based scoring automatically. No errors will crash the app.

## Performance Tips

1. **Backend optimization**: Add caching with Redis for frequently accessed data
2. **Frontend optimization**: Use React Query for data fetching; lazy-load heavy components
3. **Database**: Add indexes on `user_id`, `project_id`, `due_at` for queries
4. **AI calls**: Batch requests to OpenAI; cache results in Redis

## Resume Bullets (Fill in Later)

Once you've got the project running and tested:

- Built "TaskFlow", a cloud-ready AI-assisted task manager (FastAPI, React, PostgreSQL, Redis); delivered typed APIs, JWT auth, and Redis-backed rate limiting.
- Containerized with Docker; deployed via GitHub Actions CI/CD; integrated OpenAI GPT-4 for intelligent task prioritization; added Prometheus metrics for observability.
- Implemented database migrations (Alembic), request caching, and comprehensive tests (pytest, React Testing Library); achieved <50ms median latency on read endpoints.

## Questions?

- FastAPI Docs: https://fastapi.tiangolo.com/
- Docker Compose: https://docs.docker.com/compose/
- React: https://react.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/
- OpenAI API: https://platform.openai.com/docs/

## License

MIT
