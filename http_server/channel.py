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
            read_callback: Callable,
            write_callback: Callable,
            destroy_callback: Callable,
            args: Any
    ):
        self.sock = sock
        # self.fd = fd
        self.fd = sock.fileno()
        self.events = events
        self.read_callback = read_callback
        self.write_callback = write_callback
        self.destroy_callback = destroy_callback
        self.args = args

    def is_writeable(self):
        return self.events & constants.CHANNEL_WRITE_EVENT

    def writable(self, flag: bool):
        if flag is True:
            self.events |= constants.CHANNEL_WRITE_EVENT
        else:
            not_writable = ~constants.CHANNEL_WRITE_EVENT
            self.events &= not_writable
