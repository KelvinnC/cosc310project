from pydantic import BaseModel, Field
from typing import Union, List
from datetime import date
try:
    from pydantic import field_validator as _field_validator  # v2
    _P2 = True
except Exception:
    from pydantic import validator as _validator  # v1 fallback
    _P2 = False


class Watchlist(BaseModel):
    id: int
    authorId: Union[int, str]  # Accept both int (-1 for system) and str (UUID for users)
    movieIds: List[str]


class WatchlistRequest(BaseModel):
    movie_id: str
