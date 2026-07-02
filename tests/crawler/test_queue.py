"""Tests for crawler queue."""

from backend.app.crawler.queue import CrawlQueue, CrawlQueueItem


def test_queue_returns_items_in_fifo_order() -> None:
    """The queue keeps discovery order."""

    queue = CrawlQueue()
    first = CrawlQueueItem(url="https://example.com/", normalized_url="https://example.com/", depth=0)
    second = CrawlQueueItem(url="https://example.com/a", normalized_url="https://example.com/a", depth=1)

    queue.push(first)
    queue.push(second)

    assert len(queue) == 2
    assert queue.pop() == first
    assert queue.pop() == second
    assert not queue

