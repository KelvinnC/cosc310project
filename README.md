# Review Battle

**Team Name:** Kingfishers  
**Members:** Brad Cocar, Duncan Rabenstein, Kelvin Chen, Will Kwan
**Course:** COSC 310 - Software Engineering

A full-stack multiuser system for collaborative movie review management and competitive "review battles." Users post and vote on movie reviews, competing for the top spot on a live leaderboard. Admins moderate content and manage user penalties.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Next.js
- **Data Storage:** JSON files
- **Testing:** Pytest (90%+ coverage)
- **CI/CD:** GitHub Actions
- **Containerization:** Docker

## Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/KelvinnC/cosc310project.git
cd cosc310project
docker-compose up
```

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

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

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

## External API

Integrates with [TMDb API](https://www.themoviedb.org/documentation/api) for movie search and metadata.

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── repositories/  # Data access (JSON)
│   │   ├── schemas/       # Pydantic models
│   │   └── data/          # JSON storage files
│   └── tests/             # Pytest test suite
├── frontend/
│   ├── app/               # Next.js pages
│   └── lib/               # API utilities
├── scrum-documents/       # Sprint meeting notes
└── test-evidence/         # Coverage reports
```

## Documentation

- **API Docs:** Available at `/docs` when running
- **Project Board:** [GitHub Projects](https://github.com/users/KelvinnC/projects/1)
- **Scrum Documents:** `/scrum-documents`

## Testing

```bash
cd backend
python -m pytest --cov=app --cov-report=term-missing
```

## AI Acknowledgment

This project was developed with assistance from AI tools. All AI-generated content was reviewed, tested, and validated by team members before inclusion. Final responsibility for the code and its correctness rests with the team.
