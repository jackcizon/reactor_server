import os
import inspect
import threading
from collections import deque
from socket import socket, socketpair, AF_UNIX, SOCK_STREAM
from threading import RLock

from http_server import constants
from http_server.channel import Channel, ChannelElement
from http_server.constants import (
    CHANNEL_READ_EVENT,
    CHANNEL_WRITE_EVENT,
    EVENTLOOP_ACTION_ADD_CHANNEL,
    EVENTLOOP_ACTION_DELETE_CHANNEL,
    EVENTLOOP_ACTION_MODIFY_CHANNEL)
from http_server.dispatcher.base_dispatcher import DispatcherInterface
from http_server.dispatcher.epoll_dispatcher import EpollDispatcher


class EventLoop:
    def __init__(self, dispatcher_cls: type[DispatcherInterface] = EpollDispatcher, thread_name: str = None):
        self._is_quit = False
        self._dispatcher = dispatcher_cls(self)
        self._channel_task_queue: deque[ChannelElement] = deque()
        self._channel_map: dict[int, Channel] = {}
        self._thread_id: int | None = None  # must allocate in run()

        self._setup_thread_related(thread_name)
        self._setup_sock_pair()
        self.add_task(channel=self._new_channel(), action=constants.EVENTLOOP_ACTION_ADD_CHANNEL)

    def _setup_thread_related(self, thread_name):
        self._thread_id = None
        self._thread_name = thread_name or 'MainThread'
        self._mutex = RLock()

    def _setup_sock_pair(self):
        self._sock_pair: tuple[socket, socket] = socketpair(AF_UNIX, SOCK_STREAM)
        self._wakeup_read = self._sock_pair[0]
        self._wakeup_read_fd = self._wakeup_read.fileno()
        self._wakeup_write = self._sock_pair[1]
        self._wakeup_write_fd = self._wakeup_write.fileno()

    def _new_channel(self):
        channel = Channel(
            sock=self._wakeup_read,
            event_mask=constants.CHANNEL_READ_EVENT,
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
        self._thread_id = threading.get_ident()

        while not self._is_quit:
            self._dispatcher.dispatch()
            self._process_task_queue()

    @property
    def dispatcher(self):
        return self._dispatcher

    def event_active(self, fd: int, event_mask: int):
        channel = self._channel_map[fd]
        if event_mask & CHANNEL_READ_EVENT and channel.read_callback:
            # channel.read_callback(channel.args)
            channel.read_callback()
        if event_mask & CHANNEL_WRITE_EVENT and channel.write_callback:
            # channel.write_callback(channel.args)
            channel.write_callback()

    def add_task(self, channel: Channel, action: int):
        with self._mutex:
            self._channel_task_queue.append(ChannelElement(channel=channel, action=action))
        if self._thread_id == threading.get_ident():
            self._process_task_queue()
        else:
            self._task_wakeup()

    def _process_task_queue(self):
        """standard operation, simple to asyncio eventloop ._ready"""
        while True:
            with self._mutex:
                if not self._channel_task_queue:
                    break

                node = self._channel_task_queue.popleft()
                channel = node.channel

                if node.action == EVENTLOOP_ACTION_ADD_CHANNEL:
                    self._add(channel)
                elif node.action == EVENTLOOP_ACTION_DELETE_CHANNEL:
                    self._remove(channel)
                elif node.action == EVENTLOOP_ACTION_MODIFY_CHANNEL:
                    self._modify(channel)
                else:
                    frame = inspect.stack()[0]
                    raise RuntimeError(f'unexceptional action in {frame.function} at line {frame.lineno}')

    def _add(self, channel: Channel):
        if channel.fd not in self._channel_map.keys():
            self._channel_map[channel.fd] = channel
            self._dispatcher.set_channel(channel)
            self._dispatcher.add()

    def _remove(self, channel: Channel):
        if channel.fd in self._channel_map.keys():
            self._dispatcher.set_channel(channel)
            self._dispatcher.remove()

    def _modify(self, channel: Channel):
        if channel.fd in self._channel_map.keys():
            self._dispatcher.set_channel(channel)
            self._dispatcher.modify()

    def free_channel(self, channel: Channel):
        fd = channel.fd
        if fd in self._channel_map.keys():
            os.close(fd)
            del self._channel_map[fd]
            del channel

    @property
    def thread_id(self):
        return self._thread_id

    def _task_wakeup(self):
        os.write(self._wakeup_write_fd, bytearray(b'1'))
