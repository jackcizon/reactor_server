from os import close
from typing import Any
from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLERR, epoll

from http_server.channel import Channel
from http_server import constants
from http_server.dispatcher.base_dispatcher import AbstractDispatcher


class EpollData:
    def __init__(self, max_events: int = 1024):
        self.ep = epoll()
        self.events: list[tuple[int, int]] = []
        self.efd = self.ep.fileno()
        self.max_events = max_events


def _epoll_ctl(channel: Channel, loop, operation: int | Any):
    # get epoll instance data
    data: EpollData = loop.dispatcher_data
    events = 0

    if channel.events & constants.CHANNEL_READ_EVENT:
        events |= EPOLLIN
    if channel.events & constants.CHANNEL_WRITE_EVENT:
        events |= EPOLLOUT

    if operation == constants.EPOLL_CTL_ADD:
        data.ep.register(fd=channel.fd, eventmask=events)
    elif operation == constants.EPOLL_CTL_MOD:
        data.ep.modify(fd=channel.fd, eventmask=events)
    elif operation == constants.EPOLL_CTL_DEL:
        data.ep.unregister(channel.fd)
    else:
        raise Exception('_epoll_ctl() operation is invalid.')


class EpollDispatcher(AbstractDispatcher):
    """a handler that resolve dispatch problems"""

    def clear(self, loop):
        data: EpollData = loop.dispatcher_data
        close(data.efd)
        del data

    def add(self, channel: Channel, loop):
        _epoll_ctl(channel, loop, constants.EPOLL_CTL_ADD)

    def modify(self, channel: Channel, loop):
        _epoll_ctl(channel, loop, constants.EPOLL_CTL_MOD)

    def remove(self, channel: Channel, loop):
        _epoll_ctl(channel, loop, constants.EPOLL_CTL_DEL)
        channel.destroy_callback(channel.args)

    def dispatch(self, loop, timeout: float):
        data: EpollData = loop.dispatcher_data
        # events = data.ep.poll()
        data.events = data.ep.poll(timeout)
        for index, fd, event_mask in enumerate(data.events):
            if event_mask & EPOLLERR or event_mask & EPOLLHUP:
                continue
            if event_mask & EPOLLIN:
                event_active(loop, fd, constants.CHANNEL_READ_EVENT)
            if event_mask & EPOLLOUT:
                event_active(loop, fd, constants.CHANNEL_WRITE_EVENT)


def event_active(loop, fd, event):
    # will implement in eventloop
    pass
