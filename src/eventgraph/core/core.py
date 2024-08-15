from __future__ import annotations

from typing import TypeVar, Type, cast, Any, Generator, Optional

from mapgraph.context import InstanceContext
from mapgraph.instance_of import InstanceOf, is_instance
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
from mapgraph.type_utils import like_isinstance, like_issubclass

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
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[EventGraph[T], T]]
    _context: InstanceContext

    def add_dispatcher(
        self, event: Type[T], dispatcher: Type[BaseDispatcher[EventGraph[T], T]]
    ):
        self._dispatcher_manager.add_dispatcher(event, dispatcher)

    def remove_dispatcher(
        self,
        event: Optional[Type[T]],
        dispatcher: Optional[Type[BaseDispatcher[EventGraph[T], T]]],
    ):
        self._dispatcher_manager.remove_dispatcher(event, dispatcher)

    def get_dispatcher(
        self, event: T
    ) -> Generator[Type[BaseDispatcher[EventGraph[T], T]], Any, Any]:
        yield from self._dispatcher_manager.get_dispatcher(event)


class AnyDispatcher(Dispatcher[EventGraph[T], T]):
    @classmethod
    async def catch(cls, interface):
        if like_issubclass(EventGraph, interface.annotation):
            return interface.source
        elif like_isinstance(interface.event, interface.annotation):
            return interface.event
        raise NoCatchArgs("No catch arguments provided")


# def test(a: BaseEventGraph[BaseTask[int], EventGraph[int], int]): ...


# test(EventGraph[int]())


def init_event_graph(
    event: Type[T], context: InstanceContext = GLOBAL_INSTANCE_CONTEXT
) -> BaseEventGraph[BaseTask[T], EventGraph[T], T]:
    default_context = context

    if not is_instance(PriorityQueue[event]):
        default_context.store(PriorityQueue[event]())
    if not is_instance(ListenerManager):
        default_context.store(ListenerManager())
    if not is_instance(BaseDispatcherManager[EventGraph[event], event]):
        dm = DispatcherManager[EventGraph[event], event]()
        dm.add_dispatcher(Any, AnyDispatcher)  # type: ignore
        default_context.store(dm)

    return cast(
        BaseEventGraph[BaseTask[T], EventGraph[T], T],
        type(
            f"{event.__name__}EventGraph",
            (EventGraph,),
            {
                "_queue": InstanceOf(PriorityQueue[event]),
                "_listener_manager": InstanceOf(ListenerManager),
                "_dispatcher_manager": InstanceOf(
                    BaseDispatcherManager[EventGraph[event], event]
                ),
                "_context": default_context,
            },
        )(),
    )
