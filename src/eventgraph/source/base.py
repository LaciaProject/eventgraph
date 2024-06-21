from typing import TypeVar, Generic, Callable, Type

from ..queue.base import BaseQueue, BaseTask, PriorityQueue
from ..listener.base import ListenerManager, Listener
from ..dispatcher.base import BaseDispatcherManager, BaseDispatcher
from ..context import ContextManager
from ..instance_of import InstanceOf

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")
B_T = TypeVar("B_T")


class BaseSource(BaseDispatcherManager[S, E], Generic[T, S, E]):
    _queue: InstanceOf[BaseQueue[T]]
    _listener_manager: InstanceOf[ListenerManager]
    _context_manager: InstanceOf[ContextManager]
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[S, E]]

    def postEvent(self, event: E, priority: int = 16): ...

    def receiver(self, event: E) -> Callable: ...


BaseEventSource = BaseSource[BaseTask[B_T], S, B_T]


class EventSource(Generic[S, B_T]):
    _queue: InstanceOf[BaseQueue[BaseTask[B_T]]] = InstanceOf(PriorityQueue[B_T])
    _listener_manager = InstanceOf(ListenerManager)
    _context_manager = InstanceOf(ContextManager)
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[S, B_T]]

    def postEvent(self, event: B_T, priority: int = 16):
        self._queue.put_nowait(BaseTask(priority, event))

    def receiver(self, event: B_T):
        def receiver_wrapper(callable_target):
            listener = Listener(callable=callable_target, listening_events=[event])
            self._listener_manager.register(listener)
            return callable_target

        return receiver_wrapper

    def get_dispatcher(self, event: B_T) -> Type[BaseDispatcher[S, B_T]] | None:
        return self._dispatcher_manager.get_dispatcher(event)

    def add_dispatcher(self, event: B_T, dispatcher: Type[BaseDispatcher[S, B_T]]):
        self._dispatcher_manager.add_dispatcher(event, dispatcher)

    def remove_dispatcher(self, event: B_T, dispatcher: Type[BaseDispatcher[S, B_T]]):
        self._dispatcher_manager.remove_dispatcher(event, dispatcher)
