from typing import TypeVar, Protocol, Type, Callable, Optional, Generator, Any

from ..source.base import BaseSource
from ..executor.base import BaseExecutor
from ..context import InstanceContext, ContextManager
from ..listener.base import ListenerManager
from ..dispatcher.base import BaseDispatcherManager, BaseDispatcher
from ..queue.base import BaseQueue

from ..instance_of import InstanceOf

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")


# class BaseEventGraph(BaseSource[T, S, E], BaseExecutor[T, S, E]):
#     _context: InstanceContext


class BaseEventGraph(Protocol[T, S, E]):
    _queue: InstanceOf[BaseQueue[T]]
    _listener_manager: InstanceOf[ListenerManager]
    _context_manager: InstanceOf[ContextManager]
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[S, E]]
    _context: InstanceContext

    def start(self): ...

    async def loop(self): ...

    async def stop(self): ...

    async def execute(self, event: E): ...

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
