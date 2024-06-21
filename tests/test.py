import asyncio
from eventgraph.core.core import EventGraph, init_event_graph
from eventgraph.dispatcher.base import Dispatcher
from eventgraph.context import InstanceContext

from eventgraph.exceptions import NoCatchArgs


g = init_event_graph(int, InstanceContext())


class IntDispatcher(Dispatcher[EventGraph[int], int]):
    @classmethod
    async def catch(cls, interface):
        if interface.annotation == int:
            return interface.event
        elif interface.annotation == str:
            return "string"
        raise NoCatchArgs


@g.receiver(1)
async def test1(a: int, b: str, c=1):
    print(locals())


@g.receiver(2)
async def test2(a: int, b: str, c=1):
    print(locals())


g.add_dispatcher(1, IntDispatcher)
g.add_dispatcher(2, IntDispatcher)


async def mian():
    g.start()
    g.postEvent(1)
    g.postEvent(2)
    await g.execute(1)
    await asyncio.sleep(3)


asyncio.run(mian())
