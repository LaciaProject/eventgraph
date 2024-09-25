from __future__ import annotations

from typing import TypeVar, Type, Any, Generator, Optional

from mapgraph.context import InstanceContext
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
from mapgraph.instance_of import InstanceOf, is_instance, InstanceOfV
from typing_tool.type_utils import like_isinstance

from .base import BaseEventGraph
from ..source.base import EventSource
from ..executor.base import EventExecutor
from ..queue.base import PriorityQueue, BaseTask
from ..listener.base import ListenerManager
from ..dispatcher.base import (
    BaseDispatcherManager,
    DispatcherManager,
    Dispatcher,
    BaseDispatcher,
)
from ..exceptions import NoCatchArgs

S = TypeVar("S")
T = TypeVar("T")


class EventGraph(EventSource[T], EventExecutor[T]):
    _dispatcher_manager: InstanceOfV[BaseDispatcherManager[EventGraph[T], T]] = (
        InstanceOf(BaseDispatcherManager)
    )

    def add_dispatcher(
        self, event: Type[T], dispatcher: Type[BaseDispatcher[EventGraph[T], T]]
    ) -> None:
        self._dispatcher_manager.add_dispatcher(event, dispatcher)

    def remove_dispatcher(
        self,
        event: Optional[Type[T]],
        dispatcher: Optional[Type[BaseDispatcher[EventGraph[T], T]]],
    ) -> None:
        self._dispatcher_manager.remove_dispatcher(event, dispatcher)

    def get_dispatcher(
        self, event: T
    ) -> Generator[Type[BaseDispatcher[EventGraph[T], T]], Any, Any]:
        yield from self._dispatcher_manager.get_dispatcher(event)


class AnyDispatcher(Dispatcher[EventGraph[T], T]):
    @classmethod
    async def catch(cls, interface):
        if like_isinstance(interface.source, interface.annotation):
            return interface.source
        elif like_isinstance(interface.event, interface.annotation):
            return interface.event
        raise NoCatchArgs("No catch arguments provided")


def init_event_graph(
    event: Type[T] | Any,
    default_context: InstanceContext = GLOBAL_INSTANCE_CONTEXT,
) -> BaseEventGraph[BaseTask[T], EventGraph[T], T]:
    if not is_instance(PriorityQueue[event]):
        default_context.store(PriorityQueue[event]())
    if not is_instance(ListenerManager):
        default_context.store(ListenerManager())
    if not is_instance(BaseDispatcherManager[EventGraph[event], event]):
        dm = DispatcherManager[EventGraph[event], event]()
        dm.add_dispatcher(event, AnyDispatcher[event])
        default_context.store(dm)

    obj = EventGraph[event]()

    return obj
