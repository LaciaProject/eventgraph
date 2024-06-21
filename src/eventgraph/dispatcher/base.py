from __future__ import annotations

from typing import (
    Protocol,
    Any,
    TypeVar,
    Generic,
    MutableMapping,
    Optional,
    Type,
)
from dataclasses import dataclass

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
    _dispatchers: MutableMapping[E, Type[BaseDispatcher[S, E]]]

    def get_dispatcher(self, event: E) -> Optional[Type[BaseDispatcher[S, E]]]: ...

    def add_dispatcher(
        self, event: E, dispatcher: Type[BaseDispatcher[S, E]]
    ) -> None: ...

    def remove_dispatcher(
        self, event: Optional[E], dispatcher: Optional[Type[BaseDispatcher[S, E]]]
    ) -> None: ...


class Dispatcher(Generic[S, E]):
    @classmethod
    async def catch(cls, interface: BaseDispatcherInterface[S, E]) -> Any: ...


class DispatcherManager(Generic[S, E]):
    def __init__(self):
        self._dispatchers = {}

    def get_dispatcher(self, event: E) -> Optional[Type[BaseDispatcher[S, E]]]:
        return self._dispatchers.get(event)

    def add_dispatcher(self, event: E, dispatcher: Type[BaseDispatcher[S, E]]) -> None:
        self._dispatchers[event] = dispatcher

    def remove_dispatcher(
        self,
        event: Optional[E] = None,
        dispatcher: Optional[Type[BaseDispatcher[S, E]]] = None,
    ) -> None:
        if event is not None:
            del self._dispatchers[event]
        if dispatcher is not None:
            for key, value in self._dispatchers.items():
                if value == dispatcher:
                    del self._dispatchers[key]
