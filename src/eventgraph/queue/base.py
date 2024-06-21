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


class PriorityQueue(asyncio.PriorityQueue, Generic[V]):
    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize=maxsize)

    def put_nowait(self, item: BaseTask[V]):
        super().put_nowait((item.priority, item.data))

    def get_nowait(self) -> BaseTask[V]:
        priority, data = super().get_nowait()
        return BaseTask(priority=priority, data=data)

    async def put(self, item: BaseTask[V]) -> None:
        await super().put(item)

    async def get(self) -> BaseTask[V]:
        return await super().get()