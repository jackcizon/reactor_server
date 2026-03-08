from socket import socket

from http_server.buffer import Buffer
from http_server.channel import Channel
from http_server.constants import CHANNEL_READ_EVENT, EVENTLOOP_ACTION_ADD_CHANNEL
from http_server.eventloop import EventLoop


class Connection:
    def __init__(self, sock: socket, loop: EventLoop, name: str = None):
        self._sock = sock
        self._fd = sock.fileno()
        self._loop = loop
        self._name = name
        self._channel = Channel(
            sock=self._sock,
            event_mask=CHANNEL_READ_EVENT,
            read_callback=self.read,
            write_callback=self.write,
            destroy_callback=self.destroy,
            args=self
        )
        self._read_buf = Buffer(10240)
        self._write_buf = Buffer(10240)
        self._request = None
        self._response = None
        self._loop.add_task(channel=self._channel, action=EVENTLOOP_ACTION_ADD_CHANNEL)

    def read(self):
        count = self._read_buf.socket_read(sock=self._sock)
        if count > 0:
            # get new http request
            pass
        else:
            # disconnect
            pass

    def write(self):
        pass

    def destroy(self):
        pass
