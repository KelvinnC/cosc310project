# Deployment & Handover Guide

A comprehensive guide to deploy and maintain the Review Battle system.

---

## 1. Installation Instructions

### Prerequisites

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git**

### Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/KelvinnC/cosc310project.git
cd cosc310project

# 2. Create environment file
cp .env.example .env
# Edit .env with your credentials (see Section 3)

# 3. Build and start containers
docker-compose up --build
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stopping the System

```bash
docker-compose down
```

### Rebuilding After Changes

```bash
docker-compose up --build
```

---

## 2. Dependencies

### Backend (Python/FastAPI)

| Package | Version | Purpose |
|:--------|:--------|:--------|
| fastapi[all] | latest | Web framework with all extras (uvicorn, etc.) |
| pydantic | latest | Data validation |
| pytest | latest | Testing framework |
| pytest-mock | latest | Mocking for tests |
| pytest-asyncio | latest | Async test support |
| bcrypt | latest | Password hashing |
| PyJWT | latest | JWT authentication |
| requests | latest | HTTP client |
| httpx | latest | Async HTTP client (TMDb API) |

### Frontend (Next.js)

| Package | Version | Purpose |
|:--------|:--------|:--------|
| next | 16.0.3 | React framework |
| react | 19.2.0 | UI library |
| react-dom | 19.2.0 | React DOM rendering |
| tailwindcss | ^4 | CSS framework |
| typescript | ^5 | Type checking |

### Infrastructure

| Tool | Version | Purpose |
|:-----|:--------|:--------|
| Docker | 20.10+ | Containerization |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Python | 3.11 | Backend runtime |
| Node.js | 20 | Frontend runtime |

---

## 3. Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: JWT secret for authentication
JWT_SECRET=your-secure-random-secret-key-here

# Required: TMDb API key for movie search
TMDB_API_KEY=your-tmdb-api-key

# Optional: TMDb image base URL
TMDB_IMAGE_BASE=https://image.tmdb.org/t/p/w500
```

### Obtaining API Keys

#### TMDb API Key

1. Create an account at [themoviedb.org](https://www.themoviedb.org/signup)
2. Go to Settings → API → Request an API Key
3. Choose "Developer" and fill out the form
4. Copy the API Key (v3 auth) or API Read Access Token

---

## 4. Data Management

### Data Files

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

### Backup Procedure

```bash
# Create backup
cp -r backend/app/data backend/app/data_backup_$(date +%Y%m%d)

# Restore from backup
cp -r backend/app/data_backup_YYYYMMDD/* backend/app/data/
```

### Reset Data

To reset all data to initial state:

```bash
# Clear all JSON files (keep structure)
echo "[]" > backend/app/data/users.json
echo "[]" > backend/app/data/reviews.json
echo "[]" > backend/app/data/movies.json
echo "[]" > backend/app/data/battles.json
echo "[]" > backend/app/data/flags.json
echo "[]" > backend/app/data/comments.json
echo "[]" > backend/app/data/logs.json
```

---

## 5. Maintenance

### Logs

- **Application logs**: View in Docker with `docker-compose logs -f`
- **Audit logs**: Stored in `backend/app/data/logs.json`

### Health Check

```bash
# Check if services are running
docker-compose ps

# Check backend health
curl http://localhost:8000/docs

# Check frontend
curl http://localhost:3000
```

### Common Issues

| Issue | Solution |
|:------|:---------|
| Port 8000/3000 in use | Stop conflicting services or change ports in `docker-compose.yml` |
| TMDb search not working | Verify `TMDB_API_KEY` in `.env` is valid |
| Login not working | Ensure `JWT_SECRET` is set in `.env` |
| Data not persisting | Check volume mounts in `docker-compose.yml` |

### Updating Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

---

## 6. Account Credentials

### Default Admin Account

No default admin account is created. To create an admin:

1. Register a new user via the frontend
2. Manually edit `backend/app/data/users.json`
3. Change `"role": "user"` to `"role": "admin"`

### User Roles

| Role | Permissions |
|:-----|:------------|
| `user` | Create/edit/delete own reviews, vote in battles, flag content |
| `admin` | All user permissions + hide reviews, warn/ban users, view admin dashboard |

---

## 7. External API Reference

### TMDb API

- **Base URL**: `https://api.themoviedb.org/3`
- **Documentation**: [developer.themoviedb.org](https://developer.themoviedb.org/docs)
- **Rate Limits**: 40 requests/10 seconds
- **Used Endpoints**:
  - `GET /search/movie` — Search movies by title
  - `GET /movie/{id}` — Get movie details

---

## 8. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                             │
│                                 Port 3000                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐  │
│  │ /login  │ │ /home   │ │/reviews │ │/battles │ │/leader- │ │  /admin   │  │
│  │/register│ │(dashboard)│         │ │         │ │ board   │ │           │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────────┘  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ HTTP/REST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                              │
│                                 Port 8000                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                            ROUTERS (API Endpoints)                  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │    │
│  │  │  login   │ │  users   │ │ reviews  │ │ battles  │ │leaderboard│  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────────┘  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                │    │
│  │  │  movies  │ │   tmdb   │ │user_home │ │  admin   │                │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘                │    │
│  └─────────────────────────────────┬───────────────────────────────────┘    │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐    │
│  │                            MIDDLEWARE                               │    │
│  │  ┌──────────────────────┐  ┌──────────────────────┐                 │    │
│  │  │   auth_middleware    │  │   admin_dependency   │                 │    │
│  │  │   (JWT validation)   │  │   (role checking)    │                 │    │
│  │  └──────────────────────┘  └──────────────────────┘                 │    │
│  └─────────────────────────────────┬───────────────────────────────────┘    │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐    │
│  │                             SERVICES (Business Logic)               │    │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐           │    │
│  │  │ review_service │ │ battle_service │ │  user_service  │           │    │
│  │  └────────────────┘ └────────────────┘ └────────────────┘           │    │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐           │    │
│  │  │ movie_service  │ │  flag_service  │ │ tmdb_service   │           │    │
│  │  └────────────────┘ └────────────────┘ └────────────────┘           │    │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐           │    │
│  │  │penalty_service │ │admin_review_svc│ │ admin_user_svc │           │    │
│  │  └────────────────┘ └────────────────┘ └────────────────┘           │    │
│  │  ┌────────────────┐ ┌────────────────┐ ┌──────────────────┐         │    │
│  │  │user_login_svc  │ │user_summary_svc│ │unified_search_svc│         │    │
│  │  └────────────────┘ └────────────────┘ └──────────────────┘         │    │
│  └─────────────────────────────────┬───────────────────────────────────┘    │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐    │
│  │                          REPOSITORIES (Data Access)                 │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │ review_repo │ │ battle_repo │ │  user_repo  │ │ movie_repo  │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  │  ┌─────────────┐ ┌─────────────┐                                    │    │
│  │  │  flag_repo  │ │comment_repo │                                    │    │
│  │  └─────────────┘ └─────────────┘                                    │    │
│  └─────────────────────────────────┬───────────────────────────────────┘    │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐    │
│  │                              UTILITIES                              │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │                    Logger (Singleton)                       │    │    │
│  │  │            Thread-safe audit logging to logs.json           │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│    JSON Data Files   │  │      TMDb API        │  │     Audit Logs       │
│   (backend/app/data) │  │  (External Service)  │  │     (logs.json)      │
│  ┌────────────────┐  │  │                      │  │                      │
│  │ users.json     │  │  │  Movie search &      │  │  User actions        │
│  │ reviews.json   │  │  │  metadata retrieval  │  │  Admin actions       │
│  │ movies.json    │  │  │                      │  │  System events       │
│  │ battles.json   │  │  └──────────────────────┘  └──────────────────────┘
│  │ flags.json     │  │
│  │ comments.json  │  │
│  └────────────────┘  │
└──────────────────────┘
```

### Layer Responsibilities

| Layer | Purpose |
|:------|:--------|
| **Routers** | HTTP endpoints, request/response handling, input validation |
| **Middleware** | JWT authentication, role-based access control |
| **Services** | Business logic, data transformation, external API calls |
| **Repositories** | JSON file I/O, data persistence, CRUD operations |
| **Utilities** | Cross-cutting concerns (logging, helpers) |

---

## 9. Contact

**Team Kingfishers**
- Will Kwan
- Brad Cocar
- Kelvin Chen
- Duncan Rabenstein

**Repository**: [github.com/KelvinnC/cosc310project](https://github.com/KelvinnC/cosc310project)
