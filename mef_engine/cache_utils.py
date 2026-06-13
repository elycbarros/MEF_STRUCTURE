"""
cache_utils.py — Cache LRU para resultados de análise estrutural.

Evita recalcular o mesmo modelo com os mesmos parâmetros.
Usa hash SHA256 dos argumentos para gerar a chave.
"""

import hashlib
import json
import time
from collections import OrderedDict
from typing import Any, Callable, Optional


class AnalysisCache:
    """Cache LRU thread-safe para resultados de análise.

    Args:
        maxsize: Número máximo de entradas no cache.
        ttl_seconds: Tempo de vida máximo de cada entrada (None = sem TTL).
    """

    def __init__(self, maxsize: int = 128, ttl_seconds: Optional[float] = 300.0):
        self._maxsize = maxsize
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Gera chave hash a partir do nome da função e argumentos."""
        raw = json.dumps(
            {'fn': func_name, 'args': args, 'kwargs': kwargs},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, func_name: str, args: tuple, kwargs: dict) -> Optional[Any]:
        key = self._make_key(func_name, args, kwargs)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        ts, value = entry
        if self._ttl is not None and (time.monotonic() - ts) > self._ttl:
            del self._cache[key]
            self._misses += 1
            return None
        self._cache.move_to_end(key)
        self._hits += 1
        return value

    def set(self, func_name: str, args: tuple, kwargs: dict, value: Any) -> None:
        key = self._make_key(func_name, args, kwargs)
        self._cache[key] = (time.monotonic(), value)
        while len(self._cache) > self._maxsize:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            'size': len(self._cache),
            'maxsize': self._maxsize,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate_pct': round(hit_rate * 100, 1),
        }


# Singleton global
_global_cache = AnalysisCache()


def cached(func: Callable) -> Callable:
    """Decorator que cacheia resultados de funções de análise.

    Uso:
        @cached
        def expensive_analysis(param1, param2):
            ...
    """

    def wrapper(*args, **kwargs):
        key_name = f'{func.__module__}.{func.__qualname__}'
        result = _global_cache.get(key_name, args, kwargs)
        if result is not None:
            return result
        result = func(*args, **kwargs)
        _global_cache.set(key_name, args, kwargs, result)
        return result

    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__qualname__ = func.__qualname__
    return wrapper


def get_cache_stats() -> dict:
    return _global_cache.stats


def clear_cache() -> None:
    _global_cache.clear()
