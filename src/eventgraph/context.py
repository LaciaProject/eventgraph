from __future__ import annotations

from collections import ChainMap
from contextlib import contextmanager
from typing import Any, Mapping, MutableMapping, cast, TypeVar, Type

T = TypeVar("T")


class InstanceContext:
    instances: MutableMapping[type, Any]

    def __init__(self):
        self.instances = {}

    def store(self, *collection_or_target: Mapping[type, Any] | Any):
        for item in collection_or_target:
            if isinstance(item, Mapping):
                self.instances.update(item)
            else:
                self.instances[item.__class__] = item

    def get(self, target: Type[T]) -> T:
        return cast(T, self.instances[target])

    def is_target(self, target: Type[T]) -> bool:
        return target in self.instances

    @contextmanager
    def scope(self, *, inherit: bool = True):
        from .globals import INSTANCE_CONTEXT_VAR

        if inherit:
            res = InstanceContext()
            res.instances = ChainMap(
                {}, self.instances, INSTANCE_CONTEXT_VAR.get().instances
            )

            with res.scope(inherit=False):
                yield self
        else:
            token = INSTANCE_CONTEXT_VAR.set(self)
            try:
                yield self
            finally:
                INSTANCE_CONTEXT_VAR.reset(token)


class ContextManager:
    contexts: MutableMapping[str, InstanceContext]

    def __init__(self):
        self.contexts = {}

    def get(self, name: str) -> InstanceContext:
        return self.contexts.get(name, InstanceContext())
    
    def register(self, name: str, context: InstanceContext):
        self.contexts[name] = context

