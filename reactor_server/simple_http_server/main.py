import os

from reactor_server.simple_http_server.server import init_listen_fd, epoll_run
from reactor_server.simple_http_server.conf import BASE_DIR

if __name__ == '__main__':
    os.chdir(os.path.join(BASE_DIR))
    epoll_run(init_listen_fd())
