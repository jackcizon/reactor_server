import os
import threading
from queue import Queue
from socket import socket, socketpair, AF_UNIX, SOCK_STREAM
from threading import Lock

from http_server import constants
from http_server.channel import Channel
from http_server.dispatcher.base_dispatcher import DispatcherInterface
from http_server.dispatcher.epoll_dispatcher import EpollDispatcher


class EventLoop:
    def __init__(self, dispatcher_cls: type[DispatcherInterface] = EpollDispatcher, thread_name: str = None):
        self._is_quit = False
        self._dispatcher = dispatcher_cls()
        self._channel_task_queue = Queue()
        self._channel_map: dict[int, Channel] = {}

        self._setup_thread_related(thread_name)
        self._setup_sock_pair()
        self.add_task(channel=self._new_channel(), action=constants.EVENTLOOP_ACTION_ADD_CHANNEL)

    def _setup_thread_related(self, thread_name):
        self._thread_id = threading.get_ident()
        self._thread_name = thread_name or 'MainThread'
        self._mutex = Lock()

    def _setup_sock_pair(self):
        self._sock_pair: tuple[socket, socket] = socketpair(AF_UNIX, SOCK_STREAM)
        self._wakeup_read = self._sock_pair[1]
        self._wakeup_read_fd = self._wakeup_read.fileno()
        self._wakeup_write = self._sock_pair[0]
        self._wakeup_write_fd = self._wakeup_write.fileno()

    def _new_channel(self):
        channel = Channel(
            sock=self._wakeup_read,
            events=constants.CHANNEL_READ_EVENT,
            read_callback=self._read_message,
            write_callback=None,
            destroy_callback=None,
            args=self
        )
        return channel

    def _read_message(self):
        buf = bytearray(256)
        os.read(self._wakeup_read_fd, len(buf))

    def run(self):
        self._is_quit = False
        if self._thread_id != threading.get_ident():
            raise RuntimeError('thread error in run()')

        while not self._is_quit:
            self._dispatcher.dispatch()

    @property
    def dispatcher(self):
        return self._dispatcher

    def event_active(self, channel: Channel, event: int):
        pass

    def add_task(self, channel: Channel, action: int):
        pass

    def process_task_queue(self):
        pass

    def add(self, channel: Channel):
        pass

    def remove(self, channel: Channel):
        pass

    def modify(self, channel: Channel):
        pass

    def free_channel(self, channel: Channel):
        pass

    def get_thread_id(self):
        pass

    def _task_wakeup(self):
        pass
