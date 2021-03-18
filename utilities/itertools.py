from collections import deque
from itertools import islice


def exactly_one(iterable):
    """Obtain exactly one item from the iterable or raise an exception."""
    i = iter(iterable)
    try:
        item = next(i)
    except StopIteration:
        raise ValueError("Too few items. Expected exactly one.")
    try:
        next(i)
    except StopIteration:
        return item
    raise ValueError("Too many items. Expected exactly one.")


def consume(iterator, n=None):
    """Advance the iterator n-steps ahead. If n is None, consume entirely."""
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)


def last(iterable):
    """Obtain the last item from an iterable.

    Args:
        iterable: Any iterable series.

    Raises:
        ValueError: If the iterable is empty.
    """
    d = deque(iterable, maxlen=1)
    try:
        return d.pop()
    except IndexError:
        raise ValueError("Cannot return last item from empty iterable {!r}".format(iterable))


def deferred_chain(*iterator_factories):
    """Lazily concatenate iterable series.

    Args:
        *iterator_factories: Each iterable factory must be a zero-argument
            callable which returns an iterator when invoked.  Each factory
            will only be invoked as needed to generate the sequence, so
            may never be invoked if insufficient items are consumed.

    Returns:
        An iterator over the items produced by the iterators returns by
        invoking each iterator factory in turn.
    """
    for factory in iterator_factories:
        iterator = factory()
        yield from iterator
