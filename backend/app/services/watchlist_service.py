from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.schemas.watchlist import Watchlist
from app.repositories.watchlist_repo import load_all, save_all 
from app.repositories.movie_repo import load_all as load_all_movies

def get_watchlist_by_author_id(author_id: int) -> Optional[Watchlist]:
    watchlists = load_all()
    user_watchlist_data = next((w for w in watchlists if w["authorId"] == author_id), None)
    if user_watchlist_data is None:
        return None
    return Watchlist(**user_watchlist_data)

def add_movie_to_user_watchlist(author_id: int, movie_id: str) -> Watchlist:
    all_movies = load_all_movies()

    movie_exists = any(str(movie["id"]) == str(movie_id) for movie in all_movies)
    if not movie_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with id '{movie_id}' does not exist"
        )

    all_watchlists_data = load_all()

    user_watchlist_dict = next(
        (w for w in all_watchlists_data if w["authorId"] == author_id),
        None
    )

    if user_watchlist_dict:
        if movie_id not in user_watchlist_dict["movieIds"]:
            user_watchlist_dict["movieIds"].append(movie_id)
    else:
        new_id = max((w.get("id", 0) for w in all_watchlists_data), default=0) + 1
        user_watchlist_dict = {
            "id": new_id,
            "authorId": author_id,
            "movieIds": [movie_id]
        }
        all_watchlists_data.append(user_watchlist_dict)

    save_all(all_watchlists_data)

    return Watchlist(**user_watchlist_dict)
