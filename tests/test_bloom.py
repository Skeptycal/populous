from datetime import datetime, timedelta

from populous.bloom import BloomFilter


def test_bloom_filter():
    bf = BloomFilter()

    keys = (1, "foo", 42, "bar", 0.001, datetime.now(), None, (1, 2))
    for key in keys:
        bf.add(key)

    for key in keys:
        assert key in keys

    for key in (2, "toto", 0, datetime.now() - timedelta(hours=1)):
        assert key not in keys


def test_error_rate():
    bf = BloomFilter(step=1000, errors=0.01)

    for x in xrange(1000):
        bf.add(x)

    for x in xrange(1000):
        assert x in bf

    errors = 0
    for x in xrange(1000, 11000):
        if x in bf:
            errors += 1

    assert errors / 10000. < 0.01


def test_extend_bloom_filter():
    bf = BloomFilter(step=100)

    for key in xrange(99):
        bf.add(key)
    assert len(bf._filters) == 1

    for key in xrange(99):
        bf.add(key)
    assert len(bf._filters) == 1

    bf.add(99)
    assert len(bf._filters) == 2
    assert 42 in bf
    assert 99 in bf
    assert 100 not in bf

    for key in xrange(1000):
        bf.add(key)

    assert len(bf._filters) == 10

    for key in xrange(1000):
        assert key in bf
