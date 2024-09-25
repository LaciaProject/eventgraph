from __future__ import annotations

from typing import (
    Protocol,
    Any,
    TypeVar,
    Generic,
    Optional,
    Type,
    Generator,
)
from dataclasses import dataclass

from typing_tool.type_utils import like_isinstance

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")
B_T = TypeVar("B_T")


@dataclass
class BaseDispatcherInterface(Generic[S, E]):
    name: str
    annotation: type
    default: Any
    event: E
    source: S


class BaseDispatcher(Protocol[S, E]):
    @classmethod
    async def catch(cls, interface: BaseDispatcherInterface[S, E]) -> Any: ...


class BaseDispatcherManager(Protocol[S, E]):
    _dispatchers: list[tuple[Type[E], Type[BaseDispatcher[S, E]]]]

    def get_dispatcher(
        self, event: E
    ) -> Generator[Type[BaseDispatcher[S, E]], Any, Any]: ...

    def add_dispatcher(
        self, event: Type[E], dispatcher: Type[BaseDispatcher[S, E]]
    ) -> None: ...

    def remove_dispatcher(
        self,
        event: Optional[Type[E]],
        dispatcher: Optional[Type[BaseDispatcher[S, E]]],
    ) -> None: ...


class Dispatcher(Generic[S, E]):
    @classmethod
    async def catch(cls, interface: BaseDispatcherInterface[S, E]) -> Any: ...


class DispatcherManager(Generic[S, E]):
    _dispatchers: list[tuple[Type[E], Type[BaseDispatcher[S, E]]]]

    def __init__(self):
        self._dispatchers = []

    def get_dispatcher(
        self, event: E
    ) -> Generator[Type[BaseDispatcher[S, E]], Any, Any]:
        for k, v in self._dispatchers:
            if like_isinstance(event, k):
                yield v

    def add_dispatcher(
        self, event: Type[E], dispatcher: Type[BaseDispatcher[S, E]]
    ) -> None:
        self._dispatchers.append((event, dispatcher))

    def remove_dispatcher(
            self,
            event: Optional[Type[E]] = None,
            dispatcher: Optional[Type[BaseDispatcher[S, E]]] = None,
        ) -> None:
            to_remove = []
            if event is not None:
                for key, value in self._dispatchers:
                    if key == event:
                        to_remove.append((key, value))
            if dispatcher is not None:
                for key, value in self._dispatchers:
                    if value == dispatcher:
                        to_remove.append((key, value))
            for item in to_remove:
                self._dispatchers.remove(item)
