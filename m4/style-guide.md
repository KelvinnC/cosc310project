# Style Guide

**COSC 310 - Team Kingfishers**

Brad Cocar · Duncan Rabenstein · Will Kwan · Kelvin Chen

---

## 1. Comments & Documentation

**Rule:** Use docstrings for all public functions, classes, and API endpoints. Block comments for complex logic. Inline comments sparingly for non-obvious code.

**FastAPI Endpoints:** Every endpoint should have:
- A `summary` parameter in the decorator (short description for docs sidebar)
- A docstring (detailed description shown in expanded docs view)

```python
@router.get("/users", summary="List all users")
def get_users():
    """Retrieve all registered users in the system."""
    return list_users()
```

---

## 2. Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions & Variables | snake_case | `get_user_by_id`, `user_count` |
| Classes & Pydantic Models | PascalCase | `UserCreate`, `ReviewService` |
| Constants | UPPER_SNAKE_CASE | `MAX_REVIEWS`, `DEFAULT_LIMIT` |
| Files & Modules | snake_case | `user_endpoints.py`, `battle_service.py` |

---

## 3. Imports

**Rule:** Group imports in this order, separated by blank lines:
1. Standard library (`typing`, `json`, `datetime`)
2. Third-party packages (`fastapi`, `pydantic`)
3. Local application imports (`app.services`, `app.schemas`)

```python
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.user import User, UserCreate
from app.services.user_service import get_user_by_id
```

---

## 4. Whitespace & Indentation

**Rule:**
- Use **4 spaces** for indentation (no tabs)
- Two blank lines between top-level functions/classes
- One blank line between logical blocks within a function
- No trailing whitespace

---

## 5. Line Length & Formatting

**Rule:** Lines should not exceed **88 characters** (Black formatter default). Exceptions: imports, URLs, long strings where breaking hurts readability.

---

## 6. Type Hints

**Rule:** Use type hints for all function parameters and return types.

```python
def get_user_by_id(user_id: str) -> User:
    ...

def list_reviews(limit: int = 10, offset: int = 0) -> List[Review]:
    ...
```

---

## 7. API Response Conventions

**Rule:** Use appropriate HTTP status codes and Pydantic response models.

| Action | Status Code |
|--------|-------------|
| Create | 201 Created |
| Read | 200 OK |
| Update | 200 OK |
| Delete | 204 No Content |
| Not Found | 404 |
| Validation Error | 400/422 |
| Auth Required | 401 |
| Forbidden | 403 |
