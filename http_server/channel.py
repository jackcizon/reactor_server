from socket import socket
from typing import Any
from collections.abc import Callable

from http_server import constants


class Channel:
    def __init__(
            self,
            sock: socket,
            # fd: int,
            events: int,
            read_callback: Callable | None,
            write_callback: Callable | None,
            destroy_callback: Callable | None,
            args: Any
    ):
        self.sock = sock
        # self.fd = fd
        self._fd = sock.fileno()
        self._events = events
        self.read_callback = read_callback
        self.write_callback = write_callback
        self.destroy_callback = destroy_callback
        self._args = args

    def is_writeable(self):
        return self.events & constants.CHANNEL_WRITE_EVENT

    def writable(self, flag: bool):
        if flag is True:
            self._events |= constants.CHANNEL_WRITE_EVENT
        else:
            not_writable = ~constants.CHANNEL_WRITE_EVENT
            self._events &= not_writable

    @property
    def fd(self):
        return self._fd

    @property
    def events(self):
        return self._events

    def set_event(self, event_mask: int):
        self._events = event_mask

    @property
    def args(self):
        return self._args
