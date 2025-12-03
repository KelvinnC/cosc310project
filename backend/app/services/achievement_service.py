from collections import defaultdict
from datetime import datetime, date
from typing import Dict, List, Any

from app.repositories import review_repo, user_repo, battle_repo
from app.schemas.achievement import AchievementCategory, AchievementWinner


def _to_date(raw: Any) -> date:
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        try:
            return datetime.fromisoformat(raw).date()
        except ValueError:
            return date.min
    return date.min


def _load_usernames() -> Dict[str, str]:
    """Map user_id to username for friendly display."""
    mapping: Dict[str, str] = {}
    for user in user_repo.load_all():
        uid = str(user.get("id"))
        username = user.get("username")
        if uid and isinstance(username, str):
            mapping[uid] = username
    return mapping


def _aggregate_reviews() -> Dict[str, Dict[str, Any]]:
    """Aggregate counts, votes, and latest date per author."""
    aggregates: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "votes": 0, "latest": date.min})
    for rv in review_repo.load_all():
        author = str(rv.get("authorId"))
        agg = aggregates[author]
        agg["count"] += 1
        agg["votes"] += int(rv.get("votes") or 0)
        rv_date = _to_date(rv.get("date"))
        if rv_date > agg["latest"]:
            agg["latest"] = rv_date
    return aggregates


def _aggregate_battles() -> Dict[str, Dict[str, Any]]:
    """Aggregate battle count and latest participation per user."""
    aggregates: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "latest": date.min})
    for battle in battle_repo.load_all():
        user_id = str(battle.get("userId"))
        agg = aggregates[user_id]
        agg["count"] += 1
        ended = battle.get("endedAt") or battle.get("startedAt")
        b_date = _to_date(ended)
        if b_date > agg["latest"]:
            agg["latest"] = b_date
    return aggregates


def _pick_top_winners(
    aggregates: Dict[str, Dict[str, Any]],
    *,
    key: str,
    labels: list[str],
    category: AchievementCategory,
) -> List[AchievementWinner]:
    if not aggregates:
        return []
    user_names = _load_usernames()

    def sort_key(item):
        author, stats = item
        return (stats.get(key, 0), stats.get("latest", date.min))

    sorted_items = sorted(aggregates.items(), key=sort_key, reverse=True)[: len(labels)]
    medal_colors = {1: "gold", 2: "silver", 3: "bronze"}

    winners: List[AchievementWinner] = []
    for idx, (author, stats) in enumerate(sorted_items):
        position = idx + 1
        username = user_names.get(author, author)
        winners.append(
            AchievementWinner(
                category=category,
                userId=author,
                username=username,
                value=int(stats.get(key, 0)),
                label=labels[idx] if idx < len(labels) else labels[-1],
                position=position,
                medalColor=medal_colors.get(position),
                tieBreakDate=stats.get("latest", date.min).isoformat(),
            )
        )
    return winners


def get_achievement_winners() -> List[AchievementWinner]:
    """Return top users for each achievement category (up to 3 per category)."""
    winners: List[AchievementWinner] = []

    review_aggregates = _aggregate_reviews()
    battle_aggregates = _aggregate_battles()

    winners_map = [
        (
          review_aggregates,
          {
            "key": "votes",
            "labels": ["Best Reviews", "Great Reviews", "Good Reviews"],
            "category": AchievementCategory.MOST_VOTES,
          },
        ),
        (
          review_aggregates,
          {
            "key": "count",
            "labels": ["Top Critic", "Great Critic", "Good Critic"],
            "category": AchievementCategory.MOST_REVIEWS,
          },
        ),
        (
          battle_aggregates,
          {
            "key": "count",
            "labels": ["Top Gamer", "Great Gamer", "Good Gamer"],
            "category": AchievementCategory.MOST_BATTLES,
          },
        ),
    ]

    for aggregates, config in winners_map:
        winners.extend(_pick_top_winners(aggregates, **config))
    return winners


def get_user_badges(user_id: str) -> List[dict]:
    """Return badge descriptors for a given user_id."""
    badges = []
    for winner in get_achievement_winners():
        if str(winner.userId) == str(user_id):
            badges.append(
                {
                    "title": winner.label,
                    "description": f"{winner.label} ({winner.category.value.replace('_', ' ')})",
                    "category": winner.category.value,
                    "position": winner.position,
                    "medalColor": winner.medalColor,
                }
            )
    return badges
