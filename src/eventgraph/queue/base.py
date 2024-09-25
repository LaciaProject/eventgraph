from __future__ import annotations

import asyncio
from typing import Protocol, TypeVar, Generic

from dataclasses import dataclass


T = TypeVar("T")
V = TypeVar("V")


class BaseQueue(Protocol[T]):
    def qsize(self) -> int: ...

    def empty(self) -> bool: ...

    def full(self) -> bool: ...

    def put_nowait(self, item: T) -> None: ...

    def get_nowait(self) -> T: ...

    async def put(self, item: T) -> None: ...

    async def get(self) -> T: ...

    def task_done(self) -> None: ...

    async def join(self) -> None: ...


@dataclass
class BaseTask(Generic[V]):
    priority: int
    data: V

    def __lt__(self, other: BaseTask) -> bool:
        return self.priority < other.priority


class PriorityQueue(asyncio.PriorityQueue, Generic[V]):
    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize=maxsize)

    def qsize(self) -> int:
        return super().qsize()

    def empty(self) -> bool:
        return super().empty()

    def full(self) -> bool:
        return super().full()

    def task_done(self) -> None:
        return super().task_done()

    async def join(self) -> None:
        return await super().join()

    def put_nowait(self, item: BaseTask[V]) -> None:
        super().put_nowait(item)

    def get_nowait(self) -> BaseTask[V]:
        return super().get_nowait()

    async def put(self, item: BaseTask[V]) -> None:
        await super().put(item)

    async def get(self) -> BaseTask[V]:
        return await super().get()
