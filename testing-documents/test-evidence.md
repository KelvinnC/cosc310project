# Test Categories Evidence

Examples and references for testing approaches used in the test suite.

## 1. Integration Tests

Tests that verify multiple components work together end-to-end.

**Flag Integration** (`backend/tests/test_flag_integration.py` - Lines 13-47)
```python
# Full stack: Router → Service → Repository → File I/O
resp = client.post("/reviews/1/flag")
assert resp.status_code == 201
flags = json.loads(flags_file.read_text(encoding="utf-8"))
assert flags[0]["review_id"] == 1
reviews = json.loads(reviews_file.read_text(encoding="utf-8-sig"))
assert reviews[0]["flagged"] is True  # State changed across layers
```

**Battle E2E** (`backend/tests/test_battle_e2e.py`)
- Real subprocess server with actual HTTP requests
- Tests: Authentication → Battle creation → Voting → File persistence

---

## 2. Mocking Tests

Tests that isolate units by replacing dependencies with mocks.

**Function Mocking** (`backend/tests/test_review_service.py` - Lines 8-15)
```python
mocker.patch("app.services.review_service.load_all", return_value=[])
mocker.patch("app.repositories.movie_repo.load_all", return_value=[{"id": "UUID-movie-5678"}])
```
Isolates `create_review()` from data layer for business logic testing.

**Object Mocking** (`backend/tests/test_battle_repo.py` - Lines 10-14)
```python
mocker.patch.object(Path, "exists", return_value=False)
mocker.patch.object(Path, "exists", return_value=True)
```
Mocks filesystem behavior for error handling without real files.

**Mock Verification** (`backend/tests/test_review_service.py` - Lines 39, 72, 132)
```python
mock_save = mocker.patch("app.services.review_service.save_all")
# ... perform operation ...
mock_save.assert_called_once()  # Verify persistence was triggered
```

---

## 3. Equivalence Partitioning

Tests that cover different categories and boundaries of input values.

**Rating Classes** (`backend/tests/test_review_service_sort.py` - Lines 26-44)
```python
# Valid ratings exist
only_fives = list_reviews(rating=5)
assert len(only_fives) == 1

# No matching ratings
none_match = list_reviews(rating=999)
assert len(none_match) == 0

# Mixed ratings with ordering
asc = list_reviews(sort_by="rating", order="asc")
desc = list_reviews(sort_by="rating", order="desc")
```

**Movie ID Validity** (`backend/tests/test_review_service.py` - Lines 60-79)
```python
# Valid movieId
mocker.patch("app.repositories.movie_repo.load_all", return_value=[{"id": "UUID-movie-5678"}])
result = create_review(payload, author_id="author-1")

# Invalid movieId
mocker.patch("app.repositories.movie_repo.load_all", return_value=[{"id": "1234"}])
with pytest.raises(HTTPException):
    create_review(invalid_payload, author_id="author-1")
```

**User Authorization** (`backend/tests/test_penalty_endpoints.py` - Lines 27-65)
```python
# Warnings < 3: Can add penalty
mocker.patch("app.services.penalty_service.get_user_by_id", return_value=warned_user)

# Warnings >= 3: Reject with 400
mocker.patch("app.services.penalty_service.get_user_by_id", return_value=banned_user)
```

---

## 4. Fault Injection / Error Testing

Tests that inject failures to verify error handling.

**Missing Review** (`backend/tests/test_review_service.py` - Lines 171-179)
```python
mocker.patch("app.services.review_service.load_all", return_value=[])
mock_save = mocker.patch("app.services.review_service.save_all")

with pytest.raises(HTTPException) as ex:
    delete_review(99)

assert "not found" in str(ex.value.detail).lower()
mock_save.assert_not_called()
```

**Duplicate Flag** (`backend/tests/test_flag_integration.py` - Lines 62-85)
```python
first = client.post("/reviews/2/flag")
assert first.status_code == 201

second = client.post("/reviews/2/flag")  # Same user flags again
assert second.status_code == 409  # Conflict

flags = json.loads(flags_file.read_text(encoding="utf-8"))
assert len(flags) == 1
```

**Invalid Battle Winner** (`backend/tests/test_battle_service.py` - Lines 47-57)
```python
with pytest.raises(ValueError, match="Winner .* not in battle"):
    battle_service.submit_battle_result(
        battle,
        winner_id=99999,  # Review not in battle
        user_id=user.id
    )
```

**File I/O Failure** (`backend/tests/test_battle_repo.py` - Lines 48-55)
```python
mock_file = mock.mock_open()
mock_file.return_value.write.side_effect = OSError("Disk full")
mocker.patch.object(Path, "open", mock_file)

with pytest.raises(OSError):
    battle_repo.save_all(battle_data)
```

---

## 5. Exception Handling Tests

Tests that verify proper exception raising and HTTP status codes.

**HTTPException with Status** (`backend/tests/test_review_service.py` - Lines 113-119)
```python
mocker.patch("app.services.review_service.load_all", return_value=[])

with pytest.raises(HTTPException) as ex:
    get_review_by_id(999)

assert ex.value.status_code == 404
assert "Review not found" in ex.value.detail
```

**Multi-Status Error Handling** (`backend/tests/test_review_endpoints.py`)
```python
# 400 Bad Request
response = requests.post("/reviews", json=invalid_payload, headers=headers)
assert response.status_code == 400

# 404 Not Found
response = requests.get("/reviews/99999", headers=headers)
assert response.status_code == 404

# 409 Conflict
response = requests.post("/reviews/1/flag", headers=headers)  # First
response = requests.post("/reviews/1/flag", headers=headers)  # Second
assert response.status_code == 409
```

**Conditional Exception Mapping** (`backend/app/routers/reviews.py` - Lines 80-105)
```python
try:
    flag_record = flag_service.flag_review(user_id, review_id)
except ValueError as e:
    if "already flagged" in str(e).lower():
        raise HTTPException(status_code=409, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

**ValueError Propagation** (`backend/tests/test_battle_service.py` - Lines 53-68)
```python
with pytest.raises(ValueError) as ex:
    battle_service.submit_battle_result(battle, winner_id=99, user_id=user.id)

assert "not in battle" in str(ex.value)
# In endpoint: ValueError → 400 HTTPException
```

---

## 6. Schema Validation / Input Validation Tests

Tests that verify data validation rules and boundary conditions on input data.

**Username Length Boundaries** (`backend/tests/test_user_schema.py` - Lines 22-35)
```python
# Too short (< 3 chars)
with pytest.raises(ValidationError):
    user_copy = user_data.copy()
    user_copy["username"] = "ab"
    User(**user_copy)

# Too long (> 30 chars)
with pytest.raises(ValidationError):
    user_copy = user_data.copy()
    user_copy["username"] = "12345678901234567890abcdefghijklmnopqrstuvwxyz"
    User(**user_copy)
```

**Rating Range Validation** (`backend/tests/test_search_schema.py` - Lines 18-20)
```python
# Invalid: min_rating > max_rating
with pytest.raises(ValueError):
    MovieSearch(query="x", min_rating=8.0, max_rating=7.0)
```

**Schema Field Validation** (`backend/tests/test_battle_schema.py` - Lines 35-42)
```python
# Battle with same review1Id and review2Id raises ValidationError
battle_data["review1Id"] = 1
battle_data["review2Id"] = 1
with pytest.raises(ValidationError) as exc_info:
    Battle(**battle_data)
assert "review1Id and review2Id must be different" in str(exc_info.value)
```

---

## 7. Security & Authentication Testing

Tests that verify authentication mechanisms and security controls.

**JWT Token Expiration** (`backend/tests/test_validate_access.py` - Lines 27-30)
```python
token = create_token({"username": "expired_user"}, expired=True)
with pytest.raises(jwt.ExpiredSignatureError):
    validate_user_access(token)
```

**Token Tampering Detection** (`backend/tests/test_validate_access.py` - Lines 38-41)
```python
token = create_token({"username": "user123"})
tampered = token[:-2] + "xx"
with pytest.raises(jwt.InvalidTokenError):
    validate_user_access(tampered)
```

**Authorization Checks** (`backend/tests/test_admin_endpoints.py` - Lines 38-45)
```python
# Unauthorized user cannot access admin endpoints
response = client.get("/admin/summary")
assert response.status_code == 403
```

