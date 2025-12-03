# Requirements Fulfilment

All project requirements have been implemented (**100% completion**).

---

## Traceability Matrix

> **Key:** HLFR = High-Level Functional Requirement · US = User Story · MR = Milestone Requirement

| ID | Requirement | User Stories | Status | Implementation |
|:---|:------------|:-------------|:------:|:---------------|
| HLFR-01 | Users can register and log in | US-01, US-02 | ✅ | `routers/user_endpoints.py`, `routers/login.py`, `services/user_login_service.py` |
| HLFR-02 | Users can post, view, update, flag, delete reviews | US-03–US-07 | ✅ | `routers/reviews.py`, `services/review_service.py`, `services/flag_service.py` |
| HLFR-03 | Users can sort, filter, and download reviews | US-18, US-20 | ✅ | `routers/reviews.py`, `routers/user_home.py` |
| HLFR-04 | Users can participate in review battles | US-13 | ✅ | `routers/battles.py`, `services/battle_service.py`, `services/battle_pair_selector.py` |
| HLFR-05 | System displays leaderboard of top-voted reviews | US-15 | ✅ | `routers/leaderboard.py`, `routers/achievements.py` |
| HLFR-06 | Users can search movies and filter by rating | US-11, US-12 | ✅ | `routers/movies.py`, `services/movie_service.py`, `services/unified_search_service.py` |
| HLFR-07 | Users have personalized dashboards | US-14 | ✅ | `routers/user_home.py`, `services/user_summary_service.py` |
| HLFR-08 | Users can download personal activity history | US-18 | ✅ | `routers/user_home.py` |
| HLFR-09 | Admins can hide reviews and apply penalties | US-09, US-10, US-19 | ✅ | `services/admin_review_service.py`, `services/penalty_service.py` |
| HLFR-10 | Admins have access to admin dashboard | US-08, US-16 | ✅ | `routers/admin_endpoints.py`, `services/admin_summary_service.py` |
| HLFR-11 | System stores all data using JSON files | US-17 | ✅ | `repositories/*.py`, `data/*.json` |
| MR-01 | Thread-safe Singleton Logger for audit trail for M3 | — | ✅ | `utils/logger.py` |
| MR-02 | Integration with external TMDb API for M4 | — | ✅ | `routers/tmdb.py`, `services/tmdb_service.py` |

---

## Individual Functionality (M4)

Each team member implemented a unique feature:

| Feature | Developer | Status |
|:--------|:----------|:------:|
| Review Battles — users vote on head-to-head review matchups | Will Kwan | ✅ |
| Review Comments — users can comment on reviews | Brad Cocar | ✅ |
| Leaderboard Badges — achievement badges for top reviewers | Kelvin Chen | ✅ |
| Movie Watchlist — users can save movies to watch later | Duncan Rabenstein | ✅ |