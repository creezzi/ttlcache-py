from ttlcache import TTLCache


class Clock:
    now = 0.0

    def __call__(self):
        return self.now


def make(maxsize=2, ttl=10):
    clock = Clock()
    return TTLCache(maxsize, ttl, clock=clock), clock


def test_get_and_set():
    cache, _ = make()
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert cache.get("missing", "dflt") == "dflt"


def test_entries_expire():
    cache, clock = make(ttl=5)
    cache.set("a", 1)
    clock.now = 4.9
    assert "a" in cache
    clock.now = 5.0
    assert "a" not in cache
    assert len(cache) == 0


def test_lru_eviction_respects_recent_use():
    cache, _ = make(maxsize=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.get("a")
    cache.set("c", 3)
    assert "a" in cache and "c" in cache and "b" not in cache


def test_per_entry_ttl_and_delete():
    cache, clock = make(ttl=100)
    cache.set("a", 1, ttl=1)
    clock.now = 2
    assert cache.get("a") is None
    cache.set("b", 2)
    assert cache.delete("b") and not cache.delete("b")


def test_none_values_are_cached():
    cache, _ = make()
    cache.set("a", None)
    assert "a" in cache
