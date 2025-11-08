from app.repositories.user_repo import load_all

def get_user_count() -> int:
    users = load_all()
    return len(users)