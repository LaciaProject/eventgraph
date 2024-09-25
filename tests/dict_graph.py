import asyncio

from typing_extensions import TypedDict, Literal

from eventgraph.core.core import init_event_graph

g = init_event_graph(dict | int)


class Msg(TypedDict):
    platform: Literal["wechat", "qq"]
    content: dict


@g.receiver(dict)
async def test1(event: dict, a: int = 1):
    print(locals(), "receiver dict")


@g.receiver(Msg)
async def test2(event: Msg):
    print(locals(), "receiver Msg")


@g.receiver(int)
async def test3(event: int):
    print(locals(), "receiver int")


async def mian():
    g.start()
    g.postEvent(1, priority=36)
    g.postEvent({"platform": "wechat", "content": {"a": 1}})
    # g.postEvent({"platform": "X", "content": {"a": 1}})
    await g.execute({"platform": "X", "content": {"a": 1}})

    await asyncio.sleep(3)


asyncio.run(mian())
