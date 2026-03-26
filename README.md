# ResuHost Resume API

A FastAPI backend for managing resume data and generating PDF resumes via a Jinja2 HTML template and WeasyPrint.

## Stack

- **FastAPI** — REST API
- **SQLAlchemy** — ORM
- **PostgreSQL** — database (local or Supabase)
- **Jinja2 + WeasyPrint** — PDF generation
- **Pydantic** — request/response validation

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your database credentials.

**Supabase:**
```env
DATABASE_TARGET=supabase
SUPABASE_DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Local Postgres:**
```env
DATABASE_TARGET=local
LOCAL_DATABASE_URL=postgresql://user:password@localhost:5432/resume_db
```

### 3. Create tables

```bash
python create_database.py
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Endpoints

### Users
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/` | Create user |
| GET | `/users/` | List users |
| GET | `/users/{user_id}` | Get user |
| PUT | `/users/{user_id}` | Update user |
| DELETE | `/users/{user_id}` | Delete user |

### Experiences
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/{user_id}/experiences/` | Add experience |
| GET | `/users/{user_id}/experiences/` | List experiences |
| GET | `/users/{user_id}/experiences/{exp_id}` | Get experience |
| PUT | `/users/{user_id}/experiences/{exp_id}` | Update experience |
| DELETE | `/users/{user_id}/experiences/{exp_id}` | Delete experience |

### Education
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/{user_id}/education/` | Add education |
| GET | `/users/{user_id}/education/` | List education |
| GET | `/users/{user_id}/education/{edu_id}` | Get education |
| PUT | `/users/{user_id}/education/{edu_id}` | Update education |
| DELETE | `/users/{user_id}/education/{edu_id}` | Delete education |

### Projects
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/{user_id}/projects/` | Add project |
| GET | `/users/{user_id}/projects/` | List projects |
| GET | `/users/{user_id}/projects/{project_id}` | Get project |
| PUT | `/users/{user_id}/projects/{project_id}` | Update project |
| DELETE | `/users/{user_id}/projects/{project_id}` | Delete project |

### Activities
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/{user_id}/activities/` | Add activity |
| GET | `/users/{user_id}/activities/` | List activities |
| GET | `/users/{user_id}/activities/{activity_id}` | Get activity |
| PUT | `/users/{user_id}/activities/{activity_id}` | Update activity |
| DELETE | `/users/{user_id}/activities/{activity_id}` | Delete activity |

### Skill Categories
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/{user_id}/skill-categories/` | Add skill category |
| GET | `/users/{user_id}/skill-categories/` | List skill categories |
| GET | `/users/{user_id}/skill-categories/{category_id}` | Get skill category |
| PUT | `/users/{user_id}/skill-categories/{category_id}` | Update skill category |
| DELETE | `/users/{user_id}/skill-categories/{category_id}` | Delete skill category |

### Resume
| Method | Path | Description |
|--------|------|-------------|
| POST | `/resume/{user_id}` | Generate PDF resume |
