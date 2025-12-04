# Review Battle

**Team Kingfishers:** Brad Cocar, Duncan Rabenstein, Kelvin Chen, Will Kwan  
**Course:** COSC 310 - Software Engineering  
**Repository:** [github.com/KelvinnC/cosc310project](https://github.com/KelvinnC/cosc310project)

A full-stack multiuser system for collaborative movie review management and competitive "review battles." Users post and vote on movie reviews, competing for the top spot on a live leaderboard. Admins moderate content and manage user penalties.

---

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| Backend | FastAPI (Python 3.12) |
| Frontend | Next.js 16 / React 19 |
| Data Storage | JSON files |
| Testing | Pytest (90% coverage, 356 tests) |
| CI/CD | GitHub Actions |
| Containerization | Docker |

---

## Quick Start

### Prerequisites
- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git**

### Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/KelvinnC/cosc310project.git
cd cosc310project

# 2. Create environment file
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# 3. Build and start containers
docker-compose up --build
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Stopping & Rebuilding

```bash
docker-compose down          # Stop
docker-compose up --build    # Rebuild after changes
```

---

## Features

### Users
- **Authentication** – Register, login/logout with JWT tokens
- **Reviews** – Create, read, update, delete reviews
- **Review Battles** – Vote on head-to-head review matchups
- **Leaderboard** – Top reviews ranked by battle votes
- **Search & Filter** – Find reviews by movie, rating, or keyword
- **Flag Content** – Report inappropriate reviews for admin review
- **Dashboard** – View personal reviews, votes, and penalties
- **Data Export** – Download activity history as JSON

### Admins
- **Moderation Dashboard** – Manage flagged reviews and users
- **Hide Reviews** – Make inappropriate content invisible
- **Penalties** – Warn, suspend, or ban users
- **User Management** – View all accounts and activity

---

## Configuration

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_key
JWT_SECRET=your_jwt_secret
```

> **Note:** These credentials are available for graders in the PDF submitted by the team.

### TMDb API Key
1. Create an account at [themoviedb.org](https://www.themoviedb.org/signup)
2. Go to Settings → API → Request an API Key
3. Choose "Developer" and fill out the form
4. Copy the API Key (v3 auth) or API Read Access Token

---

## Data Management

All data is stored in JSON files under `backend/app/data/`:

| File | Purpose |
|:-----|:--------|
| `users.json` | User accounts (id, username, hashed password, role, penalties) |
| `reviews.json` | Movie reviews (id, author, movie, rating, content, votes) |
| `movies.json` | Movie metadata (id, title, year, rating) |
| `battles.json` | Review battle matchups and votes |
| `flags.json` | Flagged review reports |
| `comments.json` | Review comments |
| `logs.json` | Audit log (admin actions, user activity) |

### Backup & Reset

```bash
# Backup
cp -r backend/app/data backend/app/data_backup_$(date +%Y%m%d)

# Reset all data
echo "[]" > backend/app/data/users.json
echo "[]" > backend/app/data/reviews.json
echo "[]" > backend/app/data/movies.json
echo "[]" > backend/app/data/battles.json
echo "[]" > backend/app/data/flags.json
echo "[]" > backend/app/data/comments.json
echo "[]" > backend/app/data/logs.json
```

---

## User Roles

| Role | Permissions |
|:-----|:------------|
| `user` | Create/edit/delete own reviews, vote in battles, flag content |
| `admin` | All user permissions + hide reviews, warn/ban users, view admin dashboard |

**To create an admin:** Register a user, then manually edit `backend/app/data/users.json` and change `"role": "user"` to `"role": "admin"`.

---

## Project Structure

```
backend/
  app/
    routers/         # API endpoints
    services/        # Business logic
    repositories/    # Data access (JSON)
    schemas/         # Pydantic models
    middleware/      # Auth & admin checks
    utils/           # Logger (Singleton)
    data/            # JSON storage files
  tests/             # Pytest test suite
frontend/
  app/               # Next.js pages
  lib/               # API utilities
scrum-documents/     # Sprint meeting notes
test-evidence/       # Coverage reports
```

---

## Testing

```bash
cd backend
python -m pytest --cov=app --cov-report=term-missing
```

**Current Stats:**
- **Tests:** 356 passed
- **Coverage:** 90%
- **Runtime:** ~11 seconds

---

## Maintenance

### Health Check
```bash
docker-compose ps                    # Check running services
docker-compose logs -f               # View logs
curl http://localhost:8000/docs      # Backend health
```

### Common Issues

| Issue | Solution |
|:------|:---------|
| Port 8000/3000 in use | Stop conflicting services or change ports in `docker-compose.yml` |
| TMDb search not working | Verify `TMDB_API_KEY` in `.env` is valid |
| Login not working | Ensure `JWT_SECRET` is set in `.env` |
| Data not persisting | Check volume mounts in `docker-compose.yml` |

---

## Documentation

- **API Docs:** Available at `/docs` when running
- **Project Board:** [GitHub Projects](https://github.com/users/KelvinnC/projects/1)
- **Scrum Documents:** `/scrum-documents`

---

## External API

### TMDb API
- **Base URL:** `https://api.themoviedb.org/3`
- **Documentation:** [developer.themoviedb.org](https://developer.themoviedb.org/docs)
- **Rate Limits:** 40 requests/10 seconds
- **Used Endpoints:**
  - `GET /search/movie` — Search movies by title
  - `GET /movie/{id}` — Get movie details

---

## AI Acknowledgment

This project was developed with assistance from AI tools. All AI-generated content was reviewed, tested, and validated by team members before inclusion. Final responsibility for the code and its correctness rests with the team.
