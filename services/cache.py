from __future__ import annotations

from cachetools import TTLCache
from functools import wraps
from typing import Any, Callable

from config import settings


# Cache Configuration
cache = TTLCache(
    maxsize=100,
    ttl=settings.CACHE_TTL,
)


def cached(key_prefix: str):
    """
    Decorator for caching function results.

    Example:
        @cached("deals")
        def get_deals():
            ...
    """

    def decorator(func: Callable):

        @wraps(func)
        def wrapper(*args, **kwargs):

            key = (
                key_prefix,
                str(args),
                str(kwargs),
            )

            if key in cache:
                return cache[key]

            result = func(*args, **kwargs)

            cache[key] = result

            return result

        return wrapper

    return decorator


class CacheService:
    """
    Cache utility methods.
    """

    @staticmethod
    def get(key: str) -> Any:

        return cache.get(key)

    @staticmethod
    def set(key: str, value: Any):

        cache[key] = value

    @staticmethod
    def delete(key: str):

        cache.pop(key, None)

    @staticmethod
    def clear():

        cache.clear()

    @staticmethod
    def size() -> int:

        return len(cache)


cache_service = CacheService()