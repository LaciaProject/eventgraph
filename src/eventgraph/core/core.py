from __future__ import annotations

from typing import TypeVar, Type, cast, Any, Generator, Optional

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
from ..context import ContextManager, InstanceContext
from ..globals import GLOBAL_INSTANCE_CONTEXT
from ..instance_of import InstanceOf
from ..exceptions import NoCatchArgs

from ..type_utils import like_isinstance, like_issubclass

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
    if not default_context.is_target(PriorityQueue[event]):
        default_context.instances[PriorityQueue[event]] = PriorityQueue[event]()
    if not default_context.is_target(ListenerManager):
        default_context.instances[ListenerManager] = ListenerManager()
    if not default_context.is_target(ContextManager):
        default_context.instances[ContextManager] = ContextManager()
    if not default_context.is_target(BaseDispatcherManager[EventGraph[event], event]):
        dm = DispatcherManager[EventGraph[event]]()
        dm.add_dispatcher(Any, AnyDispatcher)  # type: ignore
        default_context.instances[BaseDispatcherManager[EventGraph[event], event]] = dm

    return cast(
        BaseEventGraph[BaseTask[T], EventGraph[T], T],
        type(
            f"{event.__name__}EventGraph",
            (EventGraph,),
            {
                "_queue": InstanceOf(PriorityQueue[event]),
                "_listener_manager": InstanceOf(ListenerManager),
                "_context_manager": InstanceOf(ContextManager),
                "_dispatcher_manager": InstanceOf(
                    BaseDispatcherManager[EventGraph[event], event]
                ),
                "_context": default_context,
            },
        )(),
    )
