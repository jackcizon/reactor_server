from reactor_server.http_server.eventloop import EventLoop
from reactor_server.http_server.server import Server

if __name__ == '__main__':
    Server(loop_cls=EventLoop, root="/home/jack/code/python/learn/reactor_server/tests").run()
