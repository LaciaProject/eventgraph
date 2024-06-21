from typing import TypeVar

from ..source.base import BaseSource
from ..executor.base import BaseExecutor
from ..queue.base import BaseTask
from ..context import InstanceContext

S = TypeVar("S")
T = TypeVar("T")
E = TypeVar("E")


class BaseEventGraph(BaseSource[T, S, E], BaseExecutor[T, S, E]):
    _context: InstanceContext

EventGraph = BaseEventGraph[BaseTask[E], S, E]
