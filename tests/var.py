import asyncio
import time

from typing import Annotated, Optional
from pydantic import Field

from typing_tool import like_issubclass, like_isinstance

from eventgraph.core.core import EventGraph, init_event_graph
from eventgraph.dispatcher.base import BaseDispatcherManager, DispatcherManager
from eventgraph.dispatcher.base import Dispatcher
from eventgraph.core.core import EventGraph
from eventgraph.core.base import BaseEventGraph
from eventgraph.queue.base import BaseQueue, BaseTask
from eventgraph.executor.base import BaseExecutor, EventExecutor


print(like_issubclass(EventExecutor[int], BaseExecutor[BaseTask[int], EventExecutor[int], int]))

# from mapgraph.context import InstanceContext
# from mapgraph.instance_of import get_instance
# from mapgraph.type_utils import like_isinstance, like_issubclass

# from eventgraph.exceptions import NoCatchArgs

# # instance_context = InstanceContext()

# instance_context.store("test")
# # instance_context.store(DispatcherManager[EventGraph[int]]())

# # g = EventGraph[int]()
# g = init_event_graph(int)


# print(like_isinstance(g, BaseEventGraph[BaseTask[int], EventGraph[int], int]))
# with instance_context.scope():
#     # print(g.__class__[int])
#     print(get_instance(BaseDispatcherManager[EventGraph[int], int]))

# event = int

# def test(a: BaseDispatcherManager[DispatcherManager[EventGraph[int]], EventGraph]): ...


# test(DispatcherManager[EventGraph[int]]())


# a = DispatcherManager[EventGraph[int]]()

# print(like_isinstance(a, BaseDispatcherManager[EventGraph[int], int]))

# print(type(None))