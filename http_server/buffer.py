import os
from socket import socket

from typing import AnyStr


class Buffer:
    def __init__(self, size: int = 4) -> None:
        self._capacity = size
        self._data = bytearray(self._capacity)
        self._read_pos = 0
        self._write_pos = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def readable_size(self) -> int:
        return self._write_pos - self._read_pos

    @property
    def writable_size(self) -> int:
        return self._capacity - self._write_pos

    @property
    def data(self) -> str:
        return self._data[self._read_pos: self._write_pos].decode()

    def _is_buf_enough(self, size: int) -> bool:
        if self.writable_size > size:
            return True
        return False

    def _can_merge(self, size: int) -> bool:
        if self._read_pos + self.writable_size >= size:
            readable_size = self.readable_size
            # mem copy
            copy_data = self._data[self._read_pos: self._write_pos]
            self._data[:readable_size] = copy_data
            # reset positions
            self._read_pos = 0
            self._write_pos = readable_size
            return True
        return False

    def _extend(self, size: int) -> None:
        self._data += bytearray(size)
        self._capacity += size

    def _try_extend(self, size: int) -> None:
        if self._is_buf_enough(size):
            return
        if self._can_merge(size):
            return
        self._extend(size)

    def append(self, buf: AnyStr) -> None:
        if isinstance(buf, str):
            buf = buf.encode()
        buf_size = len(buf)
        self._try_extend(buf_size)
        self._data[self._write_pos: self._write_pos + buf_size] = buf
        self._write_pos += buf_size

    def find_crlf(self) -> int | None:
        idx = self._data.find(b'\r\n', self._read_pos, self._write_pos)
        if idx == -1:
            return None
        return idx

    def write_view(self):
        """mem view = pointer + length + metadata"""
        return memoryview(self._data)[self._write_pos:]

    def socket_read(self, sock: socket, buf_size=40960):
        writable = self.writable_size
        tmp = bytearray(buf_size)
        n = os.readv(sock.fileno(), [self.write_view(), tmp])

        if n <= writable:
            self._write_pos += n
        else:
            self._write_pos = self._capacity
            self.append(tmp[:n - writable])
        return n

    def send_data(self, sock: socket) -> int:
        readable = self.readable_size
        if readable <= 0:
            return 0
        try:
            sent = sock.send(self._data[self._read_pos:self._write_pos])
            self._read_pos += sent
            return sent
        except (BlockingIOError, Exception):
            pass
