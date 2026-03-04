"""TTL-based caching for introspection results.

Uses stdlib only. Freqtrade codebase doesn't change during a session,
so a long TTL with manual invalidation support is appropriate.
"""

import threading
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from freqtrade_mcp.constants import DEFAULT_CACHE_TTL

P = ParamSpec("P")
R = TypeVar("R")


class TTLCache:
    """Thread-safe TTL cache for storing introspection results.

    Args:
        ttl: Time-to-live in seconds for cached entries.
    """

    def __init__(self, ttl: int = DEFAULT_CACHE_TTL) -> None:
        """Initialize the cache.

        Args:
            ttl: Time-to-live in seconds for cached entries.
        """
        self._ttl = ttl
        self._cache: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Get a value from cache if it exists and hasn't expired.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found/expired.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            timestamp, value = entry
            if time.monotonic() - timestamp > self._ttl:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        with self._lock:
            self._cache[key] = (time.monotonic(), value)

    def invalidate(self, key: str) -> None:
        """Remove a specific entry from the cache.

        Args:
            key: Cache key to remove.
        """
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        """Return the number of entries in the cache (including expired)."""
        with self._lock:
            return len(self._cache)


# Global cache instance
_global_cache = TTLCache()


def get_cache() -> TTLCache:
    """Get the global cache instance.

    Returns:
        The global TTLCache instance.
    """
    return _global_cache


def ttl_cache(ttl: int = DEFAULT_CACHE_TTL) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that caches function results with a TTL.

    Args:
        ttl: Time-to-live in seconds.

    Returns:
        Decorator function.
    """
    cache = TTLCache(ttl=ttl)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Build cache key from function name and arguments
            key_parts = [func.__qualname__]
            key_parts.extend(repr(a) for a in args)
            key_parts.extend(f"{k}={v!r}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)

            cached = cache.get(key)
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        # Expose cache for manual invalidation
        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper

    return decorator
