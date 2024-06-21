from typing import Callable, Any, overload
from dataclasses import dataclass

@dataclass
class Listener:
    callable: Callable
    listening_events: list[Any]

class ListenerManager:
    listeners: list[Listener]

    def __init__(self):
        self.listeners = []

    def getListener(self, event):
        for listener in self.listeners:
            for listening_event in listener.listening_events:
                if event == listening_event:
                    return listener
    
    def register(self, listener: Listener):
        self.listeners.append(listener)

    @overload
    def removeListener(self, listener: Listener):
        ...
    @overload
    def removeListener(self, listener: Callable):
        ...

    def removeListener(self, listener):
        remove_listener = []
        if isinstance(listener, Listener):
            remove_listener.append(listener)
        elif isinstance(listener, Callable):
            for listener in self.listeners:
                if listener.callable == listener:
                    remove_listener.append(listener)

        for listener in remove_listener:
            self.listeners.remove(listener)