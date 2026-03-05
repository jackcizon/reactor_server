"""global registry vars"""

from select import epoll
from socket import socket

sfd_socket_map: dict[int, socket] = {}
efd_epoll_map: dict[int, epoll] = {}
