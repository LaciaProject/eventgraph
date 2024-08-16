from typing import TypeVar, Protocol, Type, Callable, Optional, Generator, Any

from mapgraph.context import InstanceContext
from mapgraph.instance_of import InstanceOf

from ..listener.base import ListenerManager
from ..dispatcher.base import BaseDispatcherManager, BaseDispatcher
from ..queue.base import BaseQueue

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")


# class BaseEventGraph(BaseSource[T, S, E], BaseExecutor[T, S, E]):
#     _context: InstanceContext


class BaseEventGraph(Protocol[T, S, E]):
    _queue: InstanceOf[BaseQueue[T]]
    _listener_manager: InstanceOf[ListenerManager]
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[S, E]]
    _context: InstanceContext

    def start(self) -> None: ...

    async def loop(self) -> None: ...

    async def stop(self) -> None: ...

    async def execute(self, event: E) -> None: ...

    def postEvent(self, event: E, priority: int = 16): ...

    def receiver(self, event: Type[E] | Any) -> Callable: ...

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
