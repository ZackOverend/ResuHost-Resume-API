# ResuHost Resume API

![ResuHost Resume API](https://github.com/user-attachments/assets/c9289152-3e3b-41ce-b0db-28859d02f42c)

A FastAPI backend for managing resume data and generating PDF resumes via a Jinja2 HTML template and WeasyPrint.

## Stack

- **FastAPI** — REST API
- **SQLAlchemy** — ORM
- **PostgreSQL** — database (local or Supabase)
- **Jinja2 + WeasyPrint** — PDF generation
- **Pydantic** — request/response validation

---

## Getting Started

### Docker (recommended)

Docker bundles the API and a Postgres database together so you don't need to install or configure anything manually.

**Prerequisites:** Install [Docker Desktop](https://docs.docker.com/get-docker/) and make sure it's running before continuing.

**1. Clone the repo and enter the project folder**

```bash
git clone https://github.com/ZackOverend/ResuHost-Resume-API.git
cd ResuHost-Resume-API
```

**2. Create your environment file**

```bash
cp .env.example .env
```

The default configuration starts a local Postgres container, so no changes are needed to get started. To use Supabase instead, see the commented Supabase section in `.env.example`.

**3. Start the app**

```bash
docker compose up --build
```

This builds the API image, starts the database, creates the tables, and launches the server. It's ready when you see `Application startup complete`.

**4. Open the API**

- Interactive docs: `http://localhost:2002/docs`
- Health check: `http://localhost:2002/health`

**5. Stopping the app**

Press `Ctrl+C` in the terminal running Docker, then:

```bash
docker compose down      # stop containers, keep your data
docker compose down -v   # stop containers and wipe the database
```

### Local

**1. Install dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
# Local Postgres
DATABASE_TARGET=local
LOCAL_DATABASE_URL=postgresql://resume_user:resume_pass@db:5432/resume_db
COMPOSE_PROFILES=local

# Supabase
DATABASE_TARGET=supabase
SUPABASE_DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
COMPOSE_PROFILES=supabase
```

**3. Create tables**

```bash
python3 create_database.py
```

**4. Run the server**

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:2002/docs`.

---

## Ollama (AI tailoring)

The `/resume/{user_id}/tailor` endpoint uses Ollama to rewrite resume bullets for a given job description. Configure it via `.env` or by passing values directly in the request body.

### Environment variables

**Database**

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_TARGET` | `local` | Connection mode: `local` or `supabase` |
| `COMPOSE_PROFILES` | `local` | Controls whether Docker starts a local Postgres container (`local` or `supabase`) |
| `LOCAL_DATABASE_URL` | | Used when `DATABASE_TARGET=local` |
| `SUPABASE_DATABASE_URL` | | Used when `DATABASE_TARGET=supabase` |

**Ollama**

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://host.docker.internal:11434` | URL of your Ollama instance |
| `OLLAMA_MODEL` | `qwen3.5:cloud` | Model to use |
| `OLLAMA_API_KEY` | `ollama` | API key (only required for Ollama Cloud) |

### Deployment options

**Local Ollama running on your machine (outside Docker)**
```env
OLLAMA_HOST=http://localhost:11434
```

**Local Ollama accessed from inside Docker (default)**
```env
OLLAMA_HOST=http://host.docker.internal:11434
```

**Ollama Cloud**
```env
OLLAMA_HOST=https://api.ollama.com
OLLAMA_API_KEY=your_ollama_api_key
```

**Self-hosted remote instance**
```env
OLLAMA_HOST=http://your-server-ip:11434
```

All values can also be overridden per-request in the `POST /resume/{user_id}/tailor` request body.

---

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

### Resume & Snapshots
| Method | Path | Description |
|--------|------|-------------|
| POST | `/resume/{user_id}` | Generate PDF (`?snapshot_id=` optional) |
| POST | `/resume/{user_id}/tailor` | AI-tailor bullets to a job description |
| PATCH | `/resume/{user_id}/apply-tailor` | Write tailored bullets back to DB |
| POST | `/users/{user_id}/resumes/` | Save resume snapshot |
| GET | `/users/{user_id}/resumes/` | List snapshots |
| GET | `/users/{user_id}/resumes/{resume_id}` | Get snapshot |
| DELETE | `/users/{user_id}/resumes/{resume_id}` | Delete snapshot |
