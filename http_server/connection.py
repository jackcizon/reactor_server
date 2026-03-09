from socket import socket

from http_server.buffer import Buffer
from http_server.channel import Channel
from http_server.constants import CHANNEL_READ_EVENT, EVENTLOOP_ACTION_ADD_CHANNEL, EVENTLOOP_ACTION_DELETE_CHANNEL, \
    EVENTLOOP_ACTION_MODIFY_CHANNEL
from http_server.eventloop import EventLoop
from http_server.http.request import Request
from http_server.http.response import Response


def _debug_read_buf(read_buf):
    """inner private function for debugging"""
    print(f'--------------------------------'
          f'\n{read_buf.data}'
          f'--------------------------------')

def _debug_connection_lost():
    """inner private function for debugging"""
    print('---------------'
          'connection lost'
          '---------------')


class Connection:
    def __init__(self, sock: socket, loop: EventLoop):
        self._sock = sock
        self._fd = sock.fileno()
        self._loop = loop
        self._name = f'connection-{self._fd}'
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
        self._request = Request()
        self._response = Response()
        self._loop.add_task(channel=self._channel, action=EVENTLOOP_ACTION_ADD_CHANNEL)

    def read(self):
        count = self._read_buf.socket_read(sock=self._sock)
        if count > 0:
            # get new http request
            _debug_read_buf(self._read_buf)
            flag = self._request.parse_http_request(self._sock, self._read_buf, self._write_buf, self._response)
            if flag is None:
                self._write_buf.append('HTTP/1.1 400 Bad Request\r\n\r\n')
        else:
            self._loop.add_task(self._channel, EVENTLOOP_ACTION_DELETE_CHANNEL)
            _debug_connection_lost()

    def write(self):
        count = self._write_buf.send_data(self._channel.sock)
        if count > 0:
            if self._write_buf.readable_size > 0:
                self._channel.writable(False)
                self._loop.add_task(self._channel, EVENTLOOP_ACTION_MODIFY_CHANNEL)
                self._loop.add_task(self._channel, EVENTLOOP_ACTION_DELETE_CHANNEL)

    def destroy(self):
        if self is not None:
            del self


