# EduCore API

Production-grade Learning Management System REST API built with Django 5 and Django REST Framework.

## Features

- **Role-based access control** — Student, Instructor, Admin roles with JWT authentication
- **Course management** — Courses with ordered modules and lessons, slug-based URLs
- **Enrollment workflow** — Request → Pending → Approved/Rejected with progress tracking
- **Quiz engine** — MCQ and short-answer questions with auto-grading, retake limits, and time tracking
- **Private notes** — Per-lesson note-taking, scoped to individual users
- **Course reviews** — 1–5 star ratings with verified enrollment checks
- **Auto-certificates** — Automatically issued when a student completes 100% of a course
- **Admin dashboard** — Custom Django admin with inline editing, bulk actions, and enrollment management
- **DevOps ready** — Docker, docker-compose (Postgres + Redis), GitHub Actions CI

## Quick Start

### Local Development (SQLite)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements/dev.txt

# Copy environment config
cp .env.example .env

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Docker (Postgres + Redis)

```bash
# Start all services
docker-compose up --build

# Create admin user (in a separate terminal)
docker-compose exec app python manage.py createsuperuser
```

## API Endpoints

All endpoints are versioned under `/api/v1/`.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Create a new account |
| POST | `/api/v1/auth/login/` | Get JWT access + refresh tokens |
| POST | `/api/v1/auth/refresh/` | Refresh access token |
| GET/PUT | `/api/v1/auth/profile/` | View or update your profile |

### Courses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/courses/` | List published courses |
| POST | `/api/v1/courses/` | Create a course (instructor) |
| GET | `/api/v1/courses/{slug}/` | Course detail with modules |
| PUT/PATCH | `/api/v1/courses/{slug}/` | Update course (owner) |
| POST | `/api/v1/courses/{slug}/enroll/` | Request enrollment |
| GET/POST | `/api/v1/courses/{slug}/modules/` | List/create modules |
| GET/POST | `/api/v1/modules/{id}/lessons/` | List/create lessons |
| POST | `/api/v1/lessons/{id}/complete/` | Mark lesson completed |

### Enrollments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/enrollments/` | Manage enrollments (instructor/admin) |
| PATCH | `/api/v1/enrollments/{id}/` | Approve or reject |
| GET | `/api/v1/my-enrollments/` | Your enrollments with progress |

### Quizzes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/lessons/{id}/quiz/` | Get quiz for a lesson |
| POST | `/api/v1/lessons/{id}/quiz/create/` | Create quiz (instructor) |
| POST | `/api/v1/quizzes/{id}/attempt/` | Submit quiz answers |
| GET | `/api/v1/quizzes/{id}/attempts/` | View attempt history |

### Notes & Reviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/v1/lessons/{id}/notes/` | Your notes for a lesson |
| GET/PUT/DELETE | `/api/v1/notes/{id}/` | Manage a note |
| GET/POST | `/api/v1/courses/{slug}/reviews/` | Course reviews |
| GET/PUT/DELETE | `/api/v1/reviews/{id}/` | Manage a review |

### Certificates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/my-certificates/` | Your earned certificates |
| GET | `/api/v1/certificates/{uuid}/` | Public certificate verification |

## Project Structure

```
educore-api/
├── educore/              # Project configuration
│   ├── settings/         # Split settings (base/dev/prod)
│   ├── urls.py           # Root URL routing
│   ├── celery.py         # Async task queue
│   └── wsgi.py
├── apps/
│   ├── accounts/         # User model, JWT auth, permissions
│   ├── courses/          # Courses, modules, lessons, enrollment
│   ├── assessments/      # Quizzes, questions, attempts
│   └── content/          # Notes, reviews, certificates
├── docker/               # Dockerfile + entrypoint
├── requirements/         # Split requirements (base/dev/prod)
├── docker-compose.yml
└── .github/workflows/    # CI pipeline
```

## Running Tests

```bash
# Full test suite
pytest

# With coverage
pytest --cov=apps --cov-report=html

# Specific app
pytest apps/accounts/ -v
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` with your superuser credentials.

Features:
- Inline module and lesson editing within courses
- Bulk enrollment approval/rejection
- Completion percentage display
- Read-only quiz attempt history

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT
