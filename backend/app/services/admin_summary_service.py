from app.services.admin_review_service import get_flagged_reviews
from app.services.admin_user_service import get_banned_users, get_user_count, get_warned_users
from app.schemas.admin import AdminSummaryResponse


def get_admin_summary_data():
    return AdminSummaryResponse(
        total_users=get_user_count(),
        warned_users=get_warned_users(),
        banned_users=get_banned_users(),
        flagged_reviews=get_flagged_reviews()
    )
