# EventGraph

EventGraph 是一个现代的事件系统，旨在为 Python 应用提供高效、灵活的事件处理机制。

## 特性

- **类型安全**：利用 Python 的类型提示来确保事件处理的安全性。
- **异步支持**：原生支持异步事件处理。
- **易于扩展**：面向接口编程，易于扩展新的事件处理器。
- **上下文切换**：支持上下文切换，方便在事件处理中传递数据。
- **消息队列**：支持消息队列，意味着可以跨进程、跨机器进行事件处理。

## 快速开始

### 安装

使用 pip 安装 EventGraph：

```sh
pip install eventgraph
```

### 基本用法

1. 初始化事件图：

```python
import asyncio
from eventgraph.core.core import EventGraph, init_event_graph
from eventgraph.dispatcher.base import Dispatcher
from eventgraph.context import InstanceContext
from eventgraph.exceptions import NoCatchArgs

g = init_event_graph(int, InstanceContext())

```

2. 定义事件处理函数：

```python
@g.receiver(1)
async def test1(a: int, b: str, c=1):
    print(locals())


@g.receiver(2)
async def test2(a: int, b: str, c=1):
    print(locals())

```

3. 定义参数处理器：

```python

class IntDispatcher(Dispatcher[EventGraph[int], int]):
    @classmethod
    async def catch(cls, interface):
        if interface.annotation == int:
            return interface.event
        elif interface.annotation == str:
            return "string"
        raise NoCatchArgs

g.add_dispatcher(1, IntDispatcher)
g.add_dispatcher(2, IntDispatcher)
```

4. 发布和执行事件：

```python
async def mian():
    g.start()
    g.postEvent(1) # 发布事件
    g.postEvent(2)
    await g.execute(1) # 直接执行事件
    await asyncio.sleep(1)

asyncio.run(mian())
```

## 鸣谢

* [Graia 社区](https://github.com/GraiaProject)
* [GreyElaina](https://github.com/GreyElaina)

> 没有它们的存在就没有这个项目

## 项目灵感

* [BroadcastControl](https://github.com/GraiaProject/BroadcastControl) 
* [RvFlywheel](https://github.com/GreyElaina/RvFlywheel)