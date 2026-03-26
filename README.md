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

Open `.env` and add the following — this tells the app how to connect to the database that Docker will spin up:

```env
DATABASE_TARGET=auto
DATABASE_URL=postgresql://resume_user:resume_pass@db:5432/resume_db
```

**3. Start the app**

```bash
docker compose up --build
```

This builds the API image and starts both the API and database. Wait until you see output settle — it's ready when you see `Application startup complete`.

**4. Set up the database** (first time only)

Open a **new terminal window** in the same folder and run:

```bash
docker compose exec api python create_database.py
```

This creates the tables inside the running database container.

**5. Open the API**

- Interactive docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

**Stopping the app**

Press `Ctrl+C` in the terminal running Docker, then:

```bash
docker compose down      # stop containers, keep your data
docker compose down -v   # stop containers and wipe the database
```

### Local

**1. Install dependencies**

```bash
python -m venv venv
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
LOCAL_DATABASE_URL=postgresql://user:password@localhost:5432/resume_db

# Supabase
DATABASE_TARGET=supabase
SUPABASE_DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**3. Create tables**

```bash
python create_database.py
```

**4. Run the server**

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

---

## Ollama (AI tailoring)

When using the `/resume/{user_id}/tailor` endpoint, pass `host` in the request body:

| Context | Host value |
|---------|------------|
| Local dev | `http://localhost:11434` |
| Inside Docker | `http://host.docker.internal:11434` |
| Remote instance | `http://your-server-ip:11434` |

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
