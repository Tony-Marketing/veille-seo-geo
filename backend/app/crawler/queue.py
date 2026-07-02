"""FIFO queue used by the crawler engine."""

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlQueueItem:
    """URL waiting to be fetched."""

    url: str
    normalized_url: str
    depth: int


class CrawlQueue:
    """Small FIFO queue specialized for crawl items."""

    def __init__(self) -> None:
        self._items: deque[CrawlQueueItem] = deque()

    def push(self, item: CrawlQueueItem) -> None:
        """Append an item to the crawl queue."""

        self._items.append(item)

    def pop(self) -> CrawlQueueItem:
        """Pop the next item to fetch."""

        return self._items.popleft()

    def __bool__(self) -> bool:
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)

