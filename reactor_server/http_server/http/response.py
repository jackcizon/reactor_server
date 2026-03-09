import os
from socket import socket

from reactor_server.http_server.buffer import Buffer
from reactor_server.http_server.constants import HTTP_STATUS_CODES_MSG_MAP, STATUS_OK
from reactor_server.http_server.settings import STATIC_DIR, BASE_DIR
from reactor_server.http_server.utils import get_file_type


class Response:
    def __init__(self):
        self._status_code: int = 200
        self._filename: str | None = None
        self._headers: dict[str, str] = {}
        self._status_code_msg_map: dict[int, str] = HTTP_STATUS_CODES_MSG_MAP

    def set_status_code(self, code: int):
        self._status_code = code

    @property
    def headers(self):
        return self._headers

    def add_header(self, key: str, value: str):
        self._headers[key] = value

    def set_filename(self, name: str):
        self._filename = name

    def send_raw_headers(self, write_buf: Buffer, sock: socket):
        self._wrap_headers(write_buf)
        write_buf.send_data(sock)

    def _wrap_headers(self, write_buf):
        """from json headers to byte stream"""
        line = f'HTTP/1.1 {self._status_code} {self._status_code_msg_map[self._status_code]}\r\n'
        write_buf.append(line)
        for header_key, header_value in self._headers.items():
            # print(f'{header_key}: {header_value}')
            header_str = f'{header_key}: {header_value}\r\n'
            write_buf.append(header_str)
        write_buf.append('\r\n')

    def send_file(self, file, write_buf: Buffer, sock: socket):
        filepath = os.path.join(BASE_DIR, file)
        file_ext = file.split('.')[-1]

        fd = os.open(filepath, os.O_RDONLY)
        file_size = os.lseek(fd, 0, os.SEEK_END)
        os.lseek(fd, 0, os.SEEK_SET)

        self.add_header('Content-Type', get_file_type(file_ext))
        self.add_header('Content-Length', str(file_size))
        self.add_header("Connection", "close")

        self.send_raw_headers(write_buf, sock)

        while True:
            data = os.read(fd, 1024)
            if not data:
                break

            write_buf.append(data)
            write_buf.send_data(sock)
        os.close(fd)

    def send_dir(self, dirname: str, write_buf: Buffer, sock: socket):
        self.set_status_code(STATUS_OK)
        self.add_header('Content-Type', get_file_type('.html'))

        html: str = (f"<html>"
                     f"<head>"
                     f"<title>{dirname}</title>"
                     f"</head>"
                     f"<body><table>")
        dirpath = os.path.join(BASE_DIR, dirname)
        for item in os.scandir(dirpath):
            name = item.name
            sub_path = os.path.join(dirpath, name)
            st = os.stat(sub_path)

            if os.path.isdir(sub_path):
                line = (f'<tr>'
                        f'<td><a href="{name}/">{name}</a></td>'
                        f'<td>{st.st_size}</td>'
                        f'</tr>')
            else:
                line = (f'<tr>'
                        f'<td><a href="{name}">{name}</a></td>'
                        f'<td>{st.st_size}</td>'
                        f'</tr>')
            html += line
        html += '</table></body></html>'
        raw_html = html.encode()

        # must include this, otherwise browser 'tab' continue loading...
        self.add_header('Content-Length', str(len(raw_html)))
        self.add_header("Connection", "close")

        # send headers
        self.send_raw_headers(write_buf, sock)

        # send data
        write_buf.append(raw_html)
        write_buf.send_data(sock)

    def send_404_html(self, write_buf: Buffer, sock: socket):
        self.set_filename(os.path.join(STATIC_DIR, '404.html'))
        self.set_status_code(404)
        self.add_header('Content-Type', get_file_type('.html'))
        self.send_file(self._filename, write_buf, sock)
