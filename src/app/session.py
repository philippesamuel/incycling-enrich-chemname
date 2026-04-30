from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin

from app.config import CACHE_EXPIRE_AFTER, RATE_LIMIT_PER_SECOND


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


def build_session() -> Session:
    return CachedLimiterSession(
        per_second=RATE_LIMIT_PER_SECOND,
        expire_after=CACHE_EXPIRE_AFTER,
    )