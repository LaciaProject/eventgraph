from __future__ import annotations

import asyncio
import inspect
from typing import (
    Protocol,
    TypeVar,
    Generic,
    Type,
    Any,
    get_type_hints,
)

from mapgraph.instance_of import InstanceOf, InstanceOfV

from ..queue.base import BaseQueue, BaseTask, PriorityQueue
from ..listener.base import ListenerManager, Listener
from ..dispatcher.base import (
    BaseDispatcherManager,
    BaseDispatcherInterface,
    BaseDispatcher,
)

from ..exceptions import NoCatchArgs

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")
B_T = TypeVar("B_T")


class BaseExecutor(Protocol[T, S, E]):
    _queue: InstanceOfV[BaseQueue[T]]
    _listener_manager: InstanceOfV[ListenerManager]
    _dispatcher_manager: InstanceOfV[BaseDispatcherManager[S, E]]

    def start(self): ...

    async def loop(self): ...

    async def stop(self): ...


class EventExecutor(Generic[B_T]):
    _queue: InstanceOfV[BaseQueue[BaseTask[B_T]]] = InstanceOf(PriorityQueue[B_T])
    _listener_manager: InstanceOfV[ListenerManager] = InstanceOf(ListenerManager)
    _dispatcher_manager: InstanceOfV[BaseDispatcherManager[EventExecutor[B_T], B_T]]

    _event: asyncio.Event
    _task: asyncio.Task

    def start(self) -> None:
        if not hasattr(self, "_event"):
            self._event = asyncio.Event()
            loop = asyncio.get_event_loop()
            self._task = loop.create_task(self.loop())

    async def loop(self) -> None:
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

    async def stop(self) -> None:
        if hasattr(self, "_event"):
            self._event.set()

            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass

    async def execute(self, event: B_T) -> None:
        tasks = []
        for listener in self._listener_manager.getListener(event):
            tasks.append(self.execute_listener(event, listener))
        await asyncio.gather(*tasks)

    async def execute_listener(self, event: B_T, listener: Listener):
        args, kwargs = await self.get_args(listener.callable, event)
        return await listener.callable(*args, **kwargs)

    async def get_args(self, func, event: B_T):
        sig = inspect.signature(func)
        hints = self.get_type_hints(func, include_extras=True)
        args, kwargs = (), {}
        for name, param in sig.parameters.items():
            for dispatcher in self._dispatcher_manager.get_dispatcher(event):
                try:
                    args_value = await self.get_args_value(
                        BaseDispatcherInterface[EventExecutor[B_T], B_T](
                            name=name,
                            annotation=hints.get(name, Any),
                            default=param.default,
                            event=event,
                            source=self,
                        ),
                        dispatcher,
                    )
                    kwargs[name] = args_value
                    break
                except Exception:
                    ...
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
