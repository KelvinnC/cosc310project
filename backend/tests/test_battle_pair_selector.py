"""
Unit tests for battle_pair_selector service.

Tests the isolated logic for battle pair selection algorithms including
filtering, pair generation, and eligibility checking.
"""
import pytest
from datetime import date
from app.services import battle_pair_selector
from app.schemas.user import User
from app.schemas.review import Review


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id="user-123",
        username="testuser",
        hashed_password="hashed_pass",
        role="user",
        created_at="2025-11-01T10:00:00",
        active=True,
        warnings=0
    )


@pytest.fixture
def sample_reviews():
    """Sample reviews for testing."""
    return [
        Review(
            id=1,
            movieId="movie-1",
            authorId="author-1",
            rating=4.5,
            reviewTitle="Great movie",
            reviewBody="This movie was absolutely fantastic and I loved every minute of it.",
            flagged=False,
            votes=10,
            date=date(2025, 11, 1),
            visible=True
        ),
        Review(
            id=2,
            movieId="movie-1",
            authorId="author-2",
            rating=3.5,
            reviewTitle="Decent film",
            reviewBody="It was okay, had some good moments but also some slow parts overall.",
            flagged=False,
            votes=5,
            date=date(2025, 11, 2),
            visible=True
        ),
        Review(
            id=3,
            movieId="movie-2",
            authorId="author-3",
            rating=5.0,
            reviewTitle="Masterpiece",
            reviewBody="An absolute masterpiece that will be remembered for generations to come.",
            flagged=False,
            votes=20,
            date=date(2025, 11, 3),
            visible=True
        ),
        Review(
            id=4,
            movieId="movie-2",
            authorId="user-123",  # Owned by sample_user
            rating=4.0,
            reviewTitle="My review",
            reviewBody="This is my own review and should not appear in my battles at all.",
            flagged=False,
            votes=0,
            date=date(2025, 11, 4),
            visible=True
        )
    ]


class TestLoadUserBattles:
    """Tests for load_user_battles function."""

    def test_filters_battles_by_user_id(self, mocker):
        """Test that load_user_battles correctly filters battles by user ID."""
        all_battles = [
            {"id": "b1", "userId": "user-123", "review1Id": 1, "review2Id": 2, "winnerId": 1},
            {"id": "b2", "userId": "user-456", "review1Id": 3, "review2Id": 4, "winnerId": 3},
            {"id": "b3", "userId": "user-123", "review1Id": 5, "review2Id": 6, "winnerId": None},
            {"id": "b4", "userId": "user-789", "review1Id": 7, "review2Id": 8, "winnerId": 7}
        ]
        mocker.patch("app.repositories.battle_repo.load_all", return_value=all_battles)

        result = battle_pair_selector.load_user_battles("user-123")

        assert len(result) == 2
        assert result[0]["id"] == "b1"
        assert result[1]["id"] == "b3"
        assert all(b["userId"] == "user-123" for b in result)

    def test_returns_empty_list_when_no_battles(self, mocker):
        """Test that load_user_battles returns empty list when user has no battles."""
        mocker.patch("app.repositories.battle_repo.load_all", return_value=[])

        result = battle_pair_selector.load_user_battles("user-123")

        assert result == []

    def test_returns_empty_list_when_no_matching_user(self, mocker):
        """Test that load_user_battles returns empty list when no battles match user ID."""
        all_battles = [
            {"id": "b1", "userId": "user-456", "review1Id": 1, "review2Id": 2, "winnerId": 1},
            {"id": "b2", "userId": "user-789", "review1Id": 3, "review2Id": 4, "winnerId": 3}
        ]
        mocker.patch("app.repositories.battle_repo.load_all", return_value=all_battles)

        result = battle_pair_selector.load_user_battles("user-123")

        assert result == []

    def test_handles_none_from_load_all(self, mocker):
        """Test that load_user_battles handles None gracefully."""
        mocker.patch("app.repositories.battle_repo.load_all", return_value=None)

        result = battle_pair_selector.load_user_battles("user-123")

        assert result == []


class TestGetUserVotedPairs:
    """Tests for get_user_voted_pairs function."""

    def test_returns_frozenset_of_voted_pairs(self, mocker):
        """Test that get_user_voted_pairs returns correct frozenset of voted pairs."""
        user_battles = [
            {"id": "b1", "userId": "user-123", "review1Id": 1, "review2Id": 2, "winnerId": 1},
            {"id": "b2", "userId": "user-123", "review1Id": 3, "review2Id": 4, "winnerId": 3},
            {"id": "b3", "userId": "user-123", "review1Id": 5, "review2Id": 6, "winnerId": 5}
        ]
        mocker.patch.object(battle_pair_selector, "load_user_battles", return_value=user_battles)

        result = battle_pair_selector.get_user_voted_pairs("user-123")

        assert len(result) == 3
        assert frozenset((1, 2)) in result
        assert frozenset((3, 4)) in result
        assert frozenset((5, 6)) in result

    def test_ignores_unvoted_battles(self, mocker):
        """Test that get_user_voted_pairs ignores battles without a winner."""
        user_battles = [
            {"id": "b1", "userId": "user-123", "review1Id": 1, "review2Id": 2, "winnerId": 1},
            {"id": "b2", "userId": "user-123", "review1Id": 3, "review2Id": 4, "winnerId": None},  # No winner
            {"id": "b3", "userId": "user-123", "review1Id": 5, "review2Id": 6, "winnerId": 5}
        ]
        mocker.patch.object(battle_pair_selector, "load_user_battles", return_value=user_battles)

        result = battle_pair_selector.get_user_voted_pairs("user-123")

        assert len(result) == 2
        assert frozenset((1, 2)) in result
        assert frozenset((5, 6)) in result
        assert frozenset((3, 4)) not in result

    def test_returns_empty_set_when_no_battles(self, mocker):
        """Test that get_user_voted_pairs returns empty set when user has no battles."""
        mocker.patch.object(battle_pair_selector, "load_user_battles", return_value=[])

        result = battle_pair_selector.get_user_voted_pairs("user-123")

        assert result == set()

    def test_frozenset_is_unordered(self, mocker):
        """Test that frozenset treats (1,2) and (2,1) as the same pair."""
        user_battles = [
            {"id": "b1", "userId": "user-123", "review1Id": 1, "review2Id": 2, "winnerId": 1}
        ]
        mocker.patch.object(battle_pair_selector, "load_user_battles", return_value=user_battles)

        result = battle_pair_selector.get_user_voted_pairs("user-123")

        # Both orderings should match the same frozenset
        assert frozenset((1, 2)) in result
        assert frozenset((2, 1)) in result  # Same as (1, 2)


class TestIsOwnReview:
    """Tests for is_own_review function."""

    def test_returns_true_when_user_is_author(self, sample_user):
        """Test that is_own_review returns True when user authored the review."""
        review = Review(
            id=1,
            movieId="movie-1",
            authorId="user-123",  # Matches sample_user.id
            rating=4.5,
            reviewTitle="My review",
            reviewBody="This is my review and I wrote it with care and attention to detail.",
            flagged=False,
            votes=0,
            date=date(2025, 11, 1),
            visible=True
        )

        result = battle_pair_selector.is_own_review(sample_user, review)

        assert result is True

    def test_returns_false_when_user_is_not_author(self, sample_user):
        """Test that is_own_review returns False when user is not the author."""
        review = Review(
            id=1,
            movieId="movie-1",
            authorId="different-author",
            rating=4.5,
            reviewTitle="Someone else's review",
            reviewBody="This review was written by someone else entirely and not by the user.",
            flagged=False,
            votes=0,
            date=date(2025, 11, 1),
            visible=True
        )

        result = battle_pair_selector.is_own_review(sample_user, review)

        assert result is False

    def test_handles_integer_author_id(self, sample_user):
        """Test that is_own_review handles integer author IDs correctly."""
        review = Review(
            id=1,
            movieId="movie-1",
            authorId=-1,  # System author (integer)
            rating=4.5,
            reviewTitle="System review",
            reviewBody="This is a system generated review with an integer author identifier.",
            flagged=False,
            votes=0,
            date=date(2025, 11, 1),
            visible=True
        )

        result = battle_pair_selector.is_own_review(sample_user, review)

        assert result is False

    def test_string_comparison_is_used(self):
        """Test that author ID comparison uses string conversion."""
        user = User(
            id="123",
            username="testuser",
            hashed_password="pass",
            role="user",
            created_at="2025-11-01T10:00:00",
            active=True,
            warnings=0
        )
        review = Review(
            id=1,
            movieId="movie-1",
            authorId=123,  # Integer that should not match string "123"
            rating=4.5,
            reviewTitle="Review",
            reviewBody="This review has an integer author ID that needs string comparison.",
            flagged=False,
            votes=0,
            date=date(2025, 11, 1),
            visible=True
        )

        # String "123" != str(123) would be "123", but authorId is int 123
        result = battle_pair_selector.is_own_review(user, review)

        # The function converts authorId to string for comparison
        assert result is True


class TestFilterEligibleReviews:
    """Tests for filter_eligible_reviews function."""

    def test_excludes_user_own_reviews(self, sample_user, sample_reviews):
        """Test that filter_eligible_reviews excludes reviews by the user."""
        result = battle_pair_selector.filter_eligible_reviews(sample_user, sample_reviews)

        assert len(result) == 3
        assert all(r.id != 4 for r in result)  # Review 4 is owned by user-123
        assert all(str(r.authorId) != sample_user.id for r in result)

    def test_returns_empty_list_when_all_reviews_are_own(self, sample_user):
        """Test that filter_eligible_reviews returns empty list when all reviews are user's own."""
        own_reviews = [
            Review(
                id=i,
                movieId=f"movie-{i}",
                authorId="user-123",
                rating=4.0,
                reviewTitle=f"My review {i}",
                reviewBody=f"This is my own review number {i} with sufficient length for validation.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
            for i in range(1, 4)
        ]

        result = battle_pair_selector.filter_eligible_reviews(sample_user, own_reviews)

        assert result == []

    def test_returns_all_reviews_when_none_are_own(self, sample_user):
        """Test that filter_eligible_reviews returns all reviews when none belong to user."""
        other_reviews = [
            Review(
                id=i,
                movieId=f"movie-{i}",
                authorId=f"author-{i}",
                rating=4.0,
                reviewTitle=f"Review {i}",
                reviewBody=f"This review number {i} was written by a different author entirely.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
            for i in range(1, 4)
        ]

        result = battle_pair_selector.filter_eligible_reviews(sample_user, other_reviews)

        assert len(result) == 3

    def test_handles_empty_list(self, sample_user):
        """Test that filter_eligible_reviews handles empty review list."""
        result = battle_pair_selector.filter_eligible_reviews(sample_user, [])

        assert result == []


class TestGenerateEligiblePairs:
    """Tests for generate_eligible_pairs function."""

    def test_produces_all_unique_pairs(self, sample_reviews):
        """Test that generate_eligible_pairs produces all unique unordered pairs."""
        # With 4 reviews, should get C(4,2) = 6 pairs
        voted_pairs = set()

        result = battle_pair_selector.generate_eligible_pairs(sample_reviews, voted_pairs)

        assert len(result) == 6
        expected_pairs = [
            (1, 2), (1, 3), (1, 4),
            (2, 3), (2, 4),
            (3, 4)
        ]
        for pair in expected_pairs:
            assert pair in result

    def test_respects_voted_pairs_exclusion(self, sample_reviews):
        """Test that generate_eligible_pairs excludes already voted pairs."""
        voted_pairs = {
            frozenset((1, 2)),
            frozenset((3, 4))
        }

        result = battle_pair_selector.generate_eligible_pairs(sample_reviews, voted_pairs)

        # Should have 6 - 2 = 4 pairs remaining
        assert len(result) == 4
        assert (1, 2) not in result
        assert (3, 4) not in result
        assert (1, 3) in result
        assert (1, 4) in result
        assert (2, 3) in result
        assert (2, 4) in result

    def test_with_three_reviews_and_one_voted_pair(self):
        """Test with 3 reviews and 1 voted pair returns correct 2 remaining pairs."""
        reviews = [
            Review(
                id=i,
                movieId=f"movie-{i}",
                authorId=f"author-{i}",
                rating=4.0,
                reviewTitle=f"Review {i}",
                reviewBody=f"This is review number {i} with enough text to meet requirements.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
            for i in range(1, 4)
        ]
        voted_pairs = {frozenset((1, 2))}

        result = battle_pair_selector.generate_eligible_pairs(reviews, voted_pairs)

        # C(3,2) = 3 total pairs, minus 1 voted = 2 remaining
        assert len(result) == 2
        assert (1, 3) in result
        assert (2, 3) in result
        assert (1, 2) not in result

    def test_returns_empty_when_all_pairs_voted(self, sample_reviews):
        """Test that generate_eligible_pairs returns empty list when all pairs are voted."""
        # All possible pairs from 4 reviews
        voted_pairs = {
            frozenset((1, 2)), frozenset((1, 3)), frozenset((1, 4)),
            frozenset((2, 3)), frozenset((2, 4)),
            frozenset((3, 4))
        }

        result = battle_pair_selector.generate_eligible_pairs(sample_reviews, voted_pairs)

        assert result == []

    def test_handles_single_review(self):
        """Test that generate_eligible_pairs handles single review (no pairs possible)."""
        reviews = [
            Review(
                id=1,
                movieId="movie-1",
                authorId="author-1",
                rating=4.0,
                reviewTitle="Single review",
                reviewBody="This is the only review available in the system right now at all.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
        ]
        voted_pairs = set()

        result = battle_pair_selector.generate_eligible_pairs(reviews, voted_pairs)

        assert result == []

    def test_handles_empty_reviews(self):
        """Test that generate_eligible_pairs handles empty review list."""
        result = battle_pair_selector.generate_eligible_pairs([], set())

        assert result == []


class TestSampleReviewsForBattle:
    """Tests for sample_reviews_for_battle function."""

    def test_excludes_user_authored_reviews(self, mocker, sample_reviews):
        """Test that sample_reviews_for_battle excludes reviews by the user."""
        mocker.patch("app.services.battle_pair_selector.list_reviews", return_value=sample_reviews)

        result = battle_pair_selector.sample_reviews_for_battle("user-123", sample_size=200)

        assert len(result) == 3
        assert all(str(r.authorId) != "user-123" for r in result)

    def test_respects_sample_size_limit(self, mocker):
        """Test that sample_reviews_for_battle respects sample_size when reviews exceed limit."""
        large_review_list = [
            Review(
                id=i,
                movieId=f"movie-{i}",
                authorId=f"author-{i}",
                rating=4.0,
                reviewTitle=f"Review {i}",
                reviewBody=f"This is review number {i} with sufficient text to meet validation.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
            for i in range(1, 301)  # 300 reviews
        ]
        mocker.patch("app.services.battle_pair_selector.list_reviews", return_value=large_review_list)

        result = battle_pair_selector.sample_reviews_for_battle("other-user", sample_size=50)

        assert len(result) == 50

    def test_returns_all_when_below_sample_size(self, mocker, sample_reviews):
        """Test that sample_reviews_for_battle returns all reviews when below sample size."""
        mocker.patch("app.services.battle_pair_selector.list_reviews", return_value=sample_reviews)

        result = battle_pair_selector.sample_reviews_for_battle("user-123", sample_size=200)

        # 4 reviews minus 1 (user's own) = 3
        assert len(result) == 3

    def test_handles_empty_review_list(self, mocker):
        """Test that sample_reviews_for_battle handles empty review list."""
        mocker.patch("app.services.battle_pair_selector.list_reviews", return_value=[])

        result = battle_pair_selector.sample_reviews_for_battle("user-123", sample_size=200)

        assert result == []

    def test_handles_all_reviews_by_user(self, mocker):
        """Test that sample_reviews_for_battle handles case where all reviews are by the user."""
        user_only_reviews = [
            Review(
                id=i,
                movieId=f"movie-{i}",
                authorId="user-123",
                rating=4.0,
                reviewTitle=f"My review {i}",
                reviewBody=f"This is my own review number {i} with enough text for validation.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
            for i in range(1, 6)
        ]
        mocker.patch("app.services.battle_pair_selector.list_reviews", return_value=user_only_reviews)

        result = battle_pair_selector.sample_reviews_for_battle("user-123", sample_size=200)

        assert result == []


class TestSelectEligiblePair:
    """Tests for select_eligible_pair function."""

    def test_returns_valid_pair_tuple(self, mocker, sample_user, sample_reviews):
        """Test that select_eligible_pair returns a valid tuple of review IDs."""
        mocker.patch.object(battle_pair_selector, "get_user_voted_pairs", return_value=set())

        result = battle_pair_selector.select_eligible_pair(sample_user, sample_reviews)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)
        assert result[0] != result[1]

    def test_excludes_user_own_reviews_from_pair(self, mocker, sample_user, sample_reviews):
        """Test that select_eligible_pair never includes user's own review in the pair."""
        mocker.patch.object(battle_pair_selector, "get_user_voted_pairs", return_value=set())

        # Run multiple times to check randomness doesn't break this rule
        for _ in range(10):
            result = battle_pair_selector.select_eligible_pair(sample_user, sample_reviews)
            assert 4 not in result  # Review 4 belongs to user-123

    def test_raises_value_error_when_no_eligible_pairs(self, mocker, sample_user):
        """Test that select_eligible_pair raises ValueError when no eligible pairs available."""
        # Only user's own review
        own_reviews = [
            Review(
                id=1,
                movieId="movie-1",
                authorId="user-123",
                rating=4.0,
                reviewTitle="My review",
                reviewBody="This is my own review and there are no other reviews available.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
        ]
        mocker.patch.object(battle_pair_selector, "get_user_voted_pairs", return_value=set())

        with pytest.raises(ValueError) as exc_info:
            battle_pair_selector.select_eligible_pair(sample_user, own_reviews)

        assert "no eligible review pairs" in str(exc_info.value).lower()

    def test_raises_value_error_when_all_pairs_voted(self, mocker, sample_user):
        """Test that select_eligible_pair raises ValueError when all pairs are already voted."""
        reviews = [
            Review(
                id=i,
                movieId=f"movie-{i}",
                authorId=f"author-{i}",
                rating=4.0,
                reviewTitle=f"Review {i}",
                reviewBody=f"This is review number {i} with sufficient text for validation.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            )
            for i in range(1, 4)
        ]
        # All possible pairs from 3 reviews: (1,2), (1,3), (2,3)
        all_voted = {
            frozenset((1, 2)),
            frozenset((1, 3)),
            frozenset((2, 3))
        }
        mocker.patch.object(battle_pair_selector, "get_user_voted_pairs", return_value=all_voted)

        with pytest.raises(ValueError) as exc_info:
            battle_pair_selector.select_eligible_pair(sample_user, reviews)

        assert "no eligible review pairs" in str(exc_info.value).lower()

    def test_avoids_already_voted_pairs(self, mocker, sample_user, sample_reviews):
        """Test that select_eligible_pair avoids pairs that have already been voted on."""
        voted_pairs = {frozenset((1, 2)), frozenset((2, 3))}
        mocker.patch.object(battle_pair_selector, "get_user_voted_pairs", return_value=voted_pairs)

        # Run multiple times to ensure voted pairs are never selected
        for _ in range(10):
            result = battle_pair_selector.select_eligible_pair(sample_user, sample_reviews)
            result_set = frozenset(result)
            assert result_set not in voted_pairs

    def test_handles_minimal_case_two_reviews(self, mocker, sample_user):
        """Test that select_eligible_pair works with minimal case of exactly 2 eligible reviews."""
        reviews = [
            Review(
                id=1,
                movieId="movie-1",
                authorId="author-1",
                rating=4.0,
                reviewTitle="Review 1",
                reviewBody="This is the first review with sufficient text for validation rules.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 1),
                visible=True
            ),
            Review(
                id=2,
                movieId="movie-2",
                authorId="author-2",
                rating=4.5,
                reviewTitle="Review 2",
                reviewBody="This is the second review with sufficient text for validation rules.",
                flagged=False,
                votes=0,
                date=date(2025, 11, 2),
                visible=True
            )
        ]
        mocker.patch.object(battle_pair_selector, "get_user_voted_pairs", return_value=set())

        result = battle_pair_selector.select_eligible_pair(sample_user, reviews)

        assert set(result) == {1, 2}
