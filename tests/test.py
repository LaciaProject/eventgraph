import asyncio

from typing import Optional

from eventgraph.core.core import EventGraph, init_event_graph
from eventgraph.dispatcher.base import Dispatcher

from eventgraph.exceptions import NoCatchArgs

g = init_event_graph(int)


class Ts(int): ...


class IntDispatcher(Dispatcher[EventGraph[int], int]):
    @classmethod
    async def catch(cls, interface):
        if interface.annotation is str:
            return "string"
        raise NoCatchArgs


@g.receiver(int)
async def test1(a: int, b: str, c=1):
    print(locals(), "test1")


@g.receiver(Ts)
async def test2(a: Ts, b: str, c=1, d: Optional[EventGraph] = None):
    print(locals(), "test2")


g.add_dispatcher(int, IntDispatcher)


async def mian():
    g.start()
    g.postEvent(1)
    g.postEvent(Ts(2))
    await g.execute(Ts(1))
    await asyncio.sleep(3)


asyncio.run(mian())
