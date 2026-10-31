# ttlcache

In-memory cache with LRU eviction and per-entry time-to-live.

## Usage

```python
from ttlcache import TTLCache

cache = TTLCache(maxsize=128, ttl=30)
cache.set("user:1", {"name": "Ada"})
cache.get("user:1")  # -> {"name": "Ada"}
```

## Test

```bash
pip install pytest && pytest
```

## License

MIT
