from __future__ import annotations
from typing import TypeVar, Generic, Callable, Type, Protocol, Optional, Generator, Any

from mapgraph.instance_of import InstanceOf

from ..queue.base import BaseQueue, BaseTask, PriorityQueue
from ..listener.base import ListenerManager, Listener
from ..dispatcher.base import BaseDispatcherManager, BaseDispatcher

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")
B_T = TypeVar("B_T")


class BaseSource(Protocol[T, S, E]):
    _queue: InstanceOf[BaseQueue[T]]
    _listener_manager: InstanceOf[ListenerManager]
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[S, E]]

    def postEvent(self, event: E, priority: int = 16): ...

    def receiver(self, event: Type[E]) -> Callable: ...

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


class EventSource(Generic[B_T]):
    _queue: InstanceOf[BaseQueue[BaseTask[B_T]]] = InstanceOf(PriorityQueue[B_T])
    _listener_manager: InstanceOf[ListenerManager] = InstanceOf(ListenerManager)
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[EventSource[B_T], B_T]]

    def postEvent(self, event: B_T, priority: int = 16) -> None:
        self._queue.put_nowait(BaseTask(priority, event))

    def receiver(self, event: Type[B_T]) -> Callable:
        def receiver_wrapper(callable_target):
            listener = Listener(callable=callable_target, listening_events=[event])
            self._listener_manager.register(listener)
            return callable_target

        return receiver_wrapper

    def get_dispatcher(
        self, event: B_T
    ) -> Generator[Type[BaseDispatcher[EventSource[B_T], B_T]], Any, Any]:
        yield from self._dispatcher_manager.get_dispatcher(event)

    def add_dispatcher(
        self, event: Type[B_T], dispatcher: Type[BaseDispatcher[EventSource[B_T], B_T]]
    ):
        self._dispatcher_manager.add_dispatcher(event, dispatcher)

    def remove_dispatcher(
        self,
        event: Optional[Type[B_T]],
        dispatcher: Optional[Type[BaseDispatcher[EventSource[B_T], B_T]]],
    ):
        self._dispatcher_manager.remove_dispatcher(event, dispatcher)


# def test(a: BaseSource[BaseTask[int], EventSource[int], int]): ...


# test(EventSource[int]())
