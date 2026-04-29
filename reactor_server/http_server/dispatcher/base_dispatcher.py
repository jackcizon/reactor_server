from reactor_server.http_server.channel import Channel


class DispatcherInterface:
    """interface of dispatcher"""

    def __init__(self, *args, **kwargs):
        pass

    def add(self, channel: Channel):
        """add a channel into eventloop"""
        raise NotImplementedError

    def remove(self, channel: Channel):
        """remove related channel"""
        raise NotImplementedError

    def modify(self, channel: Channel):
        """modify channel status"""
        raise NotImplementedError

    def clear(self):
        """post operation for close fd"""
        raise NotImplementedError

    def dispatch(self):
        """monitor events"""
        raise NotImplementedError
