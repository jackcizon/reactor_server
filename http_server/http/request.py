import os
from pathlib import Path
from socket import socket

from http_server.buffer import Buffer
from http_server.constants import HTTP_PARSE_REQUEST_LINE, HTTP_PARSE_REQUEST_DONE, HTTP_PARSE_REQUEST_HEADERS, \
    HTTP_PARSE_REQUEST_BODY
from http_server.utils import get_file_type

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = os.path.join(BASE_DIR, 'static')


def _debug_process_http_request():
    print('staring processing request.')


def _debug_parse_request_line(request_line):
    """inner private function for debugging"""
    _method, _path, _version = request_line.split(' ')
    print(_method, _path, _version)


def _debug_parse_header(header_line):
    """inner private function for debugging"""
    print(f'===========try parse_headers:\n'
          f'{header_line}'
          f'\n========')
    _key, _value = header_line.split(': ')
    assert f'{_key}: {_value}' == header_line


def _debug_parse_body():
    """inner private function for debugging"""
    print('start parsing body')


class Request:
    def __init__(self):
        self._path = None
        self._method = None
        self._version = None
        self._state = HTTP_PARSE_REQUEST_LINE
        self._headers = {}

    def add_header(self, key, value):
        self._headers[key] = value

    def get_header(self, key):
        return self._headers.get(key)

    def set_method(self, method):
        self._method = method

    def set_path(self, path):
        self._path = path

    def set_version(self, version):
        self._version = version

    @property
    def state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    def parse_http_request(self, sock, read_buf, write_buf, response):
        while True:
            if self._state == HTTP_PARSE_REQUEST_LINE:
                self._parse_request_line(read_buf)
                # exit()  # debug usage
            elif self._state == HTTP_PARSE_REQUEST_HEADERS:
                self._parse_request_headers(read_buf)
                # exit()  # debug usage
            elif self._state == HTTP_PARSE_REQUEST_BODY:
                self._parse_request_body()
                # exit()  # debug usage
            elif self._state == HTTP_PARSE_REQUEST_DONE:
                # _debug_process_http_request()
                # response.prepare_message(write_buf, sock)
                break
            else:
                raise RuntimeError("Unknown HTTP PARSE STAGE.")

    def _parse_request_line(self, read_buf: Buffer):
        request_line = read_buf.read_line()
        method, path, version = request_line.split(' ')
        # _debug_parse_request_line(request_line)
        self.set_method(method)
        self.set_path(path)
        self.set_version(version)
        self.set_state(HTTP_PARSE_REQUEST_HEADERS)

    def _parse_request_headers(self, read_buf: Buffer):
        while header_line := read_buf.read_line():
            # _debug_parse_header(header_line)
            key, value = header_line.split(': ')
            self.add_header(key, value)
        self.set_state(HTTP_PARSE_REQUEST_BODY)

    def _parse_request_body(self):
        """body is empty, because server only supports [GET]"""
        # _debug_parse_body()
        self.set_state(HTTP_PARSE_REQUEST_DONE)
