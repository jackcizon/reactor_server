from enum import Enum
from typing import Any
from collections.abc import Callable


class FdEvent(Enum):
    TIMEOUT = 0b001
    READ_EVENT = 0b010
    WRITE_EVENT = 0b100


class Channel:
    def __init__(
            self,
            fd: int,
            events: int,
            read_callback: Callable,
            write_callback: Callable,
            destroy_callback: Callable,
            args: Any
    ):
        self._fd = fd
        self._events = events
        self._read_callback = read_callback
        self._write_callback = write_callback
        self._destroy_callback = destroy_callback
        self._args = args

    def is_writeable(self):
        return self._events & FdEvent.WRITE_EVENT.value

    def writable(self, flag: bool):
        if flag is True:
            self._events |= FdEvent.WRITE_EVENT.value
        else:
            not_writable = ~FdEvent.WRITE_EVENT.value
            self._events &= not_writable


if __name__ == '__main__':
    print(0b001 & 0b101)
