from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from reactor.http_server.channel import Channel
from reactor.http_server.connection import Connection
from reactor.http_server.constants import CHANNEL_READ_EVENT, EVENTLOOP_ACTION_ADD_CHANNEL
from reactor.http_server.eventloop import EventLoop
from reactor.http_server.thread.thread_pool import ThreadPool

def _debug_server_running(sock: socket):
    print(f'server running in {sock.getsockname()}')


def _debug_server_accept_connection(addr):
    print(f'new connection from: {addr}')


class Server:
    def __init__(self, loop_cls: type[EventLoop], thread_num: int, host: str = 'localhost', port: int = 8000):
        self._loop: EventLoop | None = loop_cls()
        self._thread_num = thread_num
        self._host = host
        self._port = port
        self._thread_pool = ThreadPool(self._loop, thread_num)
        self._sock: socket | None = None
        self._lfd: int | None = None

        self._setup_sock()

    def run(self):
        _debug_server_running(self._sock)
        self._thread_pool.run()
        channel = Channel(
            sock=self._sock,
            event_mask=CHANNEL_READ_EVENT,
            read_callback=self._accept_connection,
            write_callback=None,
            destroy_callback=None,
            args=self
        )
        self._loop.add_task(channel=channel, action=EVENTLOOP_ACTION_ADD_CHANNEL)
        self._loop.run()

    def _setup_sock(self):
        self._sock = socket(AF_INET, SOCK_STREAM, 0)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._sock.setblocking(False)
        self._sock.bind((self._host, self._port))
        self._sock.listen(128)
        self._lfd = self._sock.fileno()

    def _accept_connection(self):
        conn, addr = self._sock.accept()
        _debug_server_accept_connection(addr)
        loop = self._thread_pool.take_worker()
        Connection(conn, loop)
