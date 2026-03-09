import os

from reactor.http_server.eventloop import EventLoop
from reactor.http_server.server import Server
from reactor.http_server.settings import BASE_DIR

if __name__ == '__main__':
    os.chdir(os.path.join(BASE_DIR))
    Server(loop_cls=EventLoop, thread_num=10).run()
