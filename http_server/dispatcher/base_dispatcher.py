class DispatcherInterface:
    """interface of dispatcher"""

    def add(self):
        """add a channel into eventloop"""
        raise NotImplementedError

    def remove(self):
        """remove related channel"""
        raise NotImplementedError

    def modify(self):
        """modify channel status"""
        raise NotImplementedError

    def clear(self):
        """post operation for close fd"""
        raise NotImplementedError

    def dispatch(self):
        """monitor events"""
        raise NotImplementedError

    def set_channel(self, channel):
        raise NotImplementedError
