import os

from http_server.buffer import Buffer
from http_server.constants import (
    HTTP_PARSE_REQUEST_LINE,
    HTTP_PARSE_REQUEST_DONE,
    HTTP_PARSE_REQUEST_HEADERS,
    HTTP_PARSE_REQUEST_BODY)
from http_server.http.response import Response


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
        self._path: str | None = None
        self._method: str | None = None
        self._version: str | None = None
        self._state: int = HTTP_PARSE_REQUEST_LINE
        self._headers: dict[str, str] = {}

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

    @property
    def method(self):
        return self._method

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
                self._process_http_request(write_buf, response, sock)
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

    def _process_http_request(self, write_buf, response: Response, sock):
        """only allow HTTP GET"""
        # allow GET
        if self.method.upper() != 'GET':
            return None

        # is root path
        if self._path == '/':
            file = './'
        else:
            file = self._path.lstrip('/')  # e.g: /robots.txt, rm '/', get 'robots.txt'

        # file not exists
        try:
            os.stat(file)  # TODO: path security, use abspath()
        except FileNotFoundError:
            response.send_404_html(write_buf, sock)

        if os.path.isdir(file):
            response.send_dir(dirname=file, write_buf=write_buf, sock=sock)

        if os.path.isfile(file):
            response.send_file(file, write_buf, sock)
