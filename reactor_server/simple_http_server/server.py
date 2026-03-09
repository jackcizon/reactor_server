import os
import sys
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, scandir, O_RDONLY, SEEK_END, SEEK_SET
from select import EPOLLIN, EPOLLET, epoll
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, socket
from threading import Thread

from reactor_server.simple_http_server.conf import BASE_DIR, HOST, PORT, STATIC_DIR
from reactor_server.simple_http_server.log import logger

sfd_socket_map: dict[int, socket] = {}
efd_epoll_map: dict[int, epoll] = {}
tid_thread_map: dict[int, Thread] = {}


def init_listen_fd():
    global sfd_socket_map

    # init listen socket
    listen_sock = socket(AF_INET, SOCK_STREAM, 0)
    listen_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listen_sock.setblocking(False)
    listen_sock.bind((HOST, PORT))
    listen_sock.listen(128)

    # update sfd-socket map
    listen_fd = listen_sock.fileno()
    sfd_socket_map[listen_fd] = listen_sock

    # logging and helper msg
    msg = f'server running on {(HOST, PORT)}'
    logger.warning(msg)
    print(msg)

    return listen_fd


def epoll_run(lfd: int):
    global efd_epoll_map
    global tid_thread_map

    # rb-tree init
    ep = epoll()
    efd = ep.fileno()
    efd_epoll_map[efd] = ep
    ep.register(lfd, EPOLLIN | EPOLLET)

    # epoll wait
    while True:
        try:
            events: list[tuple[int, int]] = ep.poll(1)

            for sfd, event_mask in events:
                if sfd == lfd:
                    accept_client(sfd, efd)
                else:
                    recv_http_request(sfd, efd)
        finally:
            ep.unregister(lfd)
            sfd_socket_map[lfd].close()
            sys.exit()


def accept_client(lfd: int, efd: int):
    global sfd_socket_map
    global efd_epoll_map

    # get listen socket
    listen_sock = sfd_socket_map[lfd]

    # accept new connection
    conn_sock, addr = listen_sock.accept()
    conn_sock_fd = conn_sock.fileno()
    sfd_socket_map[conn_sock_fd] = conn_sock

    # set nonblocking
    flag = fcntl(conn_sock_fd, F_GETFL)
    flag |= O_NONBLOCK
    fcntl(conn_sock_fd, F_SETFL, flag | O_NONBLOCK)

    # rb-tree insert
    ep = efd_epoll_map[efd]
    ep.register(conn_sock_fd, EPOLLIN | EPOLLET)

    # logging and helper msg
    msg = f'new client from: {addr}'
    logger.warning(msg)
    print(msg)


def get_file_type(filename: str):
    ext = filename.split('.')[-1]
    ext_html_content_type_map = {
        'html': 'text/html',
        'htm': 'text/html',
        'jpg': 'image/jpg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'css': 'text/css',
        'au': 'audio/basic',
        'avi': 'audio/x-msvideo',
        'wav': 'audio/wav',
        'mpeg': 'video/mepg',
        'mp3': 'audio/mpeg',
        'txt': 'text/plain'
    }
    return ext_html_content_type_map.get(ext, 'text/plain')


def send_dir(dirname: str, conn_fd: int):
    global sfd_socket_map

    sock = sfd_socket_map[conn_fd]
    html: str = (f"<html>"
                 f"<head>"
                 f"<title>{dirname}</title>"
                 f"</head>"
                 f"<body><table>")

    dirpath = os.path.join(BASE_DIR, dirname)
    for item in scandir(dirpath):
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
    send_header_msg(conn_fd, 200, 'OK', 'text/html', len(raw_html))  # must send len first
    sock.send(raw_html, 0)


def send_404_html(conn_fd: int):
    send_file(os.path.join(STATIC_DIR, '404.html'), conn_fd)


def send_file(filename: str, conn_fd: int):
    filepath = os.path.join(BASE_DIR, filename)
    file_ext = filename.split('.')[-1]

    # read file, prepare to send its content to client(browser)
    try:
        fd = os.open(filepath, O_RDONLY)
    except Exception as e:
        # logging and helper msg
        msg = f'{e}'
        logger.warning(msg)
        print(msg)

        send_404_html(conn_fd)
        return

    file_size = os.lseek(fd, 0, SEEK_END)
    os.lseek(fd, 0, SEEK_SET)  # jump to file's zero position

    # send header
    send_header_msg(conn_fd, 200, 'OK', get_file_type(file_ext), file_size)

    offset = 0
    while offset < file_size:
        sent = os.sendfile(out_fd=conn_fd, in_fd=fd, offset=offset, count=file_size - offset)
        if sent == 0:
            break
        offset += sent
    os.close(fd)


def send_header_msg(conn_fd: int, status_code: int, desc: str, content_type: str, length: int = -1):
    """length = -1 by default if actually cannot get the length"""
    global sfd_socket_map

    header = (f'HTTP/1.1 {status_code} {desc}\r\n'
              f'Content-Type: {content_type}\r\n'
              f'Content-Length: {length}\r\n'
              f'Connection: close\r\n'
              f'\r\n')
    sock = sfd_socket_map[conn_fd]
    sock.send(header.encode(), 0)


def recv_http_request(conn_fd: int, efd: int):
    global sfd_socket_map

    sock = sfd_socket_map[conn_fd]
    ep = efd_epoll_map[efd]

    total_data = bytearray()
    try:
        while True:
            chunk = sock.recv(1024)

            if not chunk:
                ep.unregister(conn_fd)
                sock.close()
                del sfd_socket_map[conn_fd]
                return
            total_data.extend(chunk)

    except BlockingIOError:
        pos = total_data.find(b'\r\n')
        # if b'\r\n' not in total_data:
        #     return  # 等下次 epoll 再读
        request_line = total_data[:pos].decode()
        parse_request_line(request_line, conn_fd)

    except Exception as e:
        # logging and helper msg
        msg = f'{e}'
        logger.warning(msg)
        print(msg)

        # handle close
        ep.unregister(conn_fd)
        sock.close()
        del sfd_socket_map[conn_fd]


def parse_request_line(line: str, conn_fd: int):
    global sfd_socket_map

    try:
        method, path, version = line.split()
        print(line)
    except ValueError as e:
        # logging and helper msg
        msg = f'{e}'
        logger.error(msg)
        print(msg)
        raise ValueError(f'http request line parse error')

    if method.lower() != 'get':
        raise Exception('only support http get')

    if path == '/':
        file = './'
    else:
        file = path.lstrip('/')

    if os.path.isdir(file):
        send_dir(dirname=file, conn_fd=conn_fd)
    else:
        send_file(file, conn_fd)

    # logging and helper msg
    sock = sfd_socket_map[conn_fd]
    msg = f'conn_fd: {sock.getpeername()} visited {path}'
    logger.info(msg)
    print(msg)
