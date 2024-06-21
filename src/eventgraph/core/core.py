from __future__ import annotations

from typing import TypeVar, Type, cast
from typing_extensions import Self

from eventgraph.dispatcher.base import BaseDispatcher

from ..source.base import EventSource
from ..executor.base import EventExecutor

from ..queue.base import PriorityQueue, BaseQueue, BaseTask
from ..listener.base import ListenerManager
from ..dispatcher.base import BaseDispatcherManager, DispatcherManager, Dispatcher

from ..context import ContextManager, InstanceContext
from ..globals import GLOBAL_INSTANCE_CONTEXT
from ..instance_of import InstanceOf

S = TypeVar("S")
T = TypeVar("T")


class EventGraph(
    EventSource[EventSource[T, T], T], EventExecutor[EventExecutor[T, T], T]
):
    _queue: InstanceOf[BaseQueue[BaseTask[T]]] = InstanceOf(PriorityQueue[T])
    _listener_manager = InstanceOf(ListenerManager)
    _context_manager = InstanceOf(ContextManager)
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[EventGraph[T], T]]
    _context: InstanceContext

    def add_dispatcher(self, event: T, dispatcher: Type[Dispatcher[EventGraph[T], T]]):
        self._dispatcher_manager.add_dispatcher(event, dispatcher)

    def remove_dispatcher(
        self, event: T, dispatcher: Type[Dispatcher[EventGraph[T], T]]
    ):
        self._dispatcher_manager.remove_dispatcher(event, dispatcher)

    def get_dispatcher(self, event: T) -> Type[BaseDispatcher[EventGraph[T], T]] | None:
        return self._dispatcher_manager.get_dispatcher(event)


def init_event_graph(
    event: Type[T], context: InstanceContext = GLOBAL_INSTANCE_CONTEXT
) -> EventGraph[T]:
    default_context = context
    if not default_context.is_target(PriorityQueue[event]):
        default_context.instances[PriorityQueue[event]] = PriorityQueue[event]()
    if not default_context.is_target(ListenerManager):
        default_context.instances[ListenerManager] = ListenerManager()
    if not default_context.is_target(ContextManager):
        default_context.instances[ContextManager] = ContextManager()
    if not default_context.is_target(BaseDispatcherManager[BaseTask[event], event]):
        default_context.instances[BaseDispatcherManager[BaseTask[event], event]] = (
            DispatcherManager[event, EventGraph]()
        )

    return cast(
        EventGraph[T],
        type(
            f"{event.__name__}EventGraph",
            (EventGraph,),
            {
                "_queue": InstanceOf(PriorityQueue[event]),
                "_listener_manager": InstanceOf(ListenerManager),
                "_context_manager": InstanceOf(ContextManager),
                "_dispatcher_manager": InstanceOf(
                    BaseDispatcherManager[BaseTask[event], event]
                ),
                "_context": default_context,
            },
        )(),
    )
