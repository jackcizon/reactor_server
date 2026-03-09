import os
from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLERR, epoll

from reactor_server.http_server.channel import Channel
from reactor_server.http_server import constants
from reactor_server.http_server.dispatcher.base_dispatcher import DispatcherInterface


class EpollDispatcher(DispatcherInterface):
    """a handler that resolve dispatch problems"""

    def __init__(self, loop, *args, name: str = "epoll", timeout: float = 2.0, max_events: int = 1024, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = loop
        self._name = name
        self._timeout = timeout
        self._channel: Channel | None = None
        self.ep = epoll()
        self.events: list[tuple[int, int]] = []
        self.efd = self.ep.fileno()
        self.max_events = max_events

    def clear(self):
        os.close(self.efd)
        del self

    def _epoll_ctl(self, operation: int):
        event_mask = 0
        if self._channel.event_mask & constants.CHANNEL_READ_EVENT:
            event_mask |= EPOLLIN
        if self._channel.event_mask & constants.CHANNEL_WRITE_EVENT:
            event_mask |= EPOLLOUT

        if operation == constants.EPOLL_CTL_ADD:
            self.ep.register(fd=self._channel.fd, eventmask=event_mask)
        elif operation == constants.EPOLL_CTL_MOD:
            self.ep.modify(fd=self._channel.fd, eventmask=event_mask)
        elif operation == constants.EPOLL_CTL_DEL:
            self.ep.unregister(self._channel.fd)
        else:
            raise Exception('_epoll_ctl() operation is invalid.')

    def add(self):
        self._epoll_ctl(constants.EPOLL_CTL_ADD)

    def modify(self):
        self._epoll_ctl(constants.EPOLL_CTL_MOD)

    def remove(self):
        self._epoll_ctl(constants.EPOLL_CTL_DEL)
        # self._channel.destroy_callback(self._channel.args)
        self._channel.destroy_callback()

    def dispatch(self):
        try:
            self.events = self.ep.poll(self._timeout)
            events = self.events
            for fd, event_mask in events:
                if event_mask & EPOLLERR or event_mask & EPOLLHUP:
                    continue
                if event_mask & EPOLLIN:
                    self._loop.event_active(fd, constants.CHANNEL_READ_EVENT)
                if event_mask & EPOLLOUT:
                    self._loop.event_active(fd, constants.CHANNEL_WRITE_EVENT)
        except (KeyboardInterrupt, Exception):
            exit()

    def set_channel(self, channel: Channel):
        """
        set dispatcher's channel instance,
        this method will only call in eventloop,
        similar to Future() in asyncio.eventloop.
        """
        self._channel = channel
