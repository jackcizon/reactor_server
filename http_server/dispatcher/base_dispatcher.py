from http_server.channel import Channel


class AbstractDispatcher:
    """abstract dispatcher"""

    def add(self, channel: Channel, loop):
        """add a channel into eventloop"""
        raise NotImplementedError

    def remove(self, channel: Channel, loop):
        """remove related channel"""
        raise NotImplementedError

    def modify(self, channel: Channel, loop):
        """modify channel status"""
        raise NotImplementedError

    def clear(self, loop):
        """post operation for close fd"""
        raise NotImplementedError

    def dispatch(self, loop, timeout: float):
        """monitor events"""
        raise NotImplementedError
