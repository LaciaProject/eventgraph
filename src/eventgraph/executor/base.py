import asyncio
import inspect
from typing import Protocol, TypeVar, Generic, Type, Any, get_type_hints

from ..queue.base import BaseQueue, BaseTask, PriorityQueue
from ..listener.base import ListenerManager
from ..dispatcher.base import (
    BaseDispatcherManager,
    BaseDispatcherInterface,
    BaseDispatcher,
)
from ..context import ContextManager
from ..instance_of import InstanceOf

from ..exceptions import NoCatchArgs

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")
B_T = TypeVar("B_T")


class BaseExecutor(Protocol[T, S, E]):
    _queue: InstanceOf[BaseQueue[T]]
    _listener_manager: InstanceOf[ListenerManager]
    _context_manager: InstanceOf[ContextManager]
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[S, E]]

    def start(self): ...

    async def loop(self): ...

    async def stop(self): ...

    async def execute(self, event: E): ...


BaseEventExecutor = BaseExecutor[BaseTask[B_T], S, B_T]


class EventExecutor(Generic[S, B_T]):
    _queue: InstanceOf[BaseQueue[BaseTask[B_T]]] = InstanceOf(PriorityQueue[B_T])
    _listener_manager = InstanceOf(ListenerManager)
    _context_manager = InstanceOf(ContextManager)
    _dispatcher_manager: InstanceOf[BaseDispatcherManager[S, B_T]]

    _event: asyncio.Event
    _task: asyncio.Task

    def start(self):
        if not hasattr(self, "_event"):
            self._event = asyncio.Event()
            loop = asyncio.get_event_loop()
            self._task = loop.create_task(self.loop())

    async def loop(self):
        try:
            loop = asyncio.get_event_loop()
            while not self._event.is_set():
                try:
                    task = await self._queue.get()
                    loop.create_task(self.execute(task.data))
                except asyncio.CancelledError:
                    break
        finally:
            await self.stop()

    async def stop(self):
        if hasattr(self, "_event"):
            self._event.set()

            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass

    async def execute(self, event: B_T):
        listener = self._listener_manager.getListener(event)
        if listener:
            args, kwargs = await self.get_args(listener.callable, event)
            await listener.callable(*args, **kwargs)

    async def get_args(self, func, event: B_T):
        sig = inspect.signature(func)
        hints = self.get_type_hints(func, include_extras=True)
        args, kwargs = (), {}
        dispatcher = self._dispatcher_manager.get_dispatcher(event)
        if not dispatcher:
            return args, kwargs

        for name, param in sig.parameters.items():
            kwargs[name] = await self.get_args_value(
                BaseDispatcherInterface[S, B_T](
                    name=name,
                    annotation=hints.get(name, Any),
                    default=param.default,
                    event=event,
                    source=self,  # type: ignore
                ),
                dispatcher,
            )
        bound = sig.bind(*args, **kwargs)
        return bound.args, bound.kwargs

    async def get_args_value(
        self,
        interface: BaseDispatcherInterface[S, B_T],
        dispatcher: Type[BaseDispatcher[S, B_T]],
    ):
        try:
            res = await dispatcher.catch(interface)
        except NoCatchArgs:
            if interface.default is inspect.Parameter.empty:
                raise NoCatchArgs(f"{interface.name} is required")
            res = interface.default

        return res

    def get_type_hints(
        self,
        func,
        globalns: dict[str, Any] | None = None,
        localns: dict[str, Any] | None = None,
        include_extras: bool = False,
    ):
        return get_type_hints(
            func, globalns=globalns, localns=localns, include_extras=include_extras
        )
