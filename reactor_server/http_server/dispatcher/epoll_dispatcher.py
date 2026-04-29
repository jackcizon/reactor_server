from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLERR, epoll

from reactor_server.http_server import constants
from reactor_server.http_server.channel import Channel
from reactor_server.http_server.dispatcher.base_dispatcher import DispatcherInterface


class EpollDispatcher(DispatcherInterface):
    """a handler that resolve dispatch problems"""

    def __init__(self, loop, *args, name: str = "epoll", timeout: float = 2.0, max_events: int = 1024, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = loop
        self._name = name
        self._timeout = timeout
        self.ep = epoll()
        self.events: list[tuple[int, int]] = []
        self.efd = self.ep.fileno()
        self.max_events = max_events

    def _epoll_ctl(self, channel: Channel, operation: int):
        event_mask = 0
        if channel.is_readable():
            event_mask |= EPOLLIN
        if channel.is_writable():
            event_mask |= EPOLLOUT

        if operation == constants.EPOLL_CTL_ADD:
            self.ep.register(fd=channel.fd, eventmask=event_mask)
        elif operation == constants.EPOLL_CTL_MOD:
            self.ep.modify(fd=channel.fd, eventmask=event_mask)
        elif operation == constants.EPOLL_CTL_DEL:
            self.ep.unregister(channel.fd)
        else:
            raise Exception('_epoll_ctl() operation is invalid.')

    def add(self, channel: Channel):
        self._epoll_ctl(channel, constants.EPOLL_CTL_ADD)

    def modify(self, channel: Channel):
        self._epoll_ctl(channel, constants.EPOLL_CTL_MOD)

    def remove(self, channel: Channel):
        self._epoll_ctl(channel, constants.EPOLL_CTL_DEL)
        # channel.destroy_callback(channel.args)
        channel.destroy_callback()

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
