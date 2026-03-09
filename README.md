# reactor

**A minimal HTTP server implementing the Reactor pattern in Python.
Designed for learning event-driven network programming.**

This project aims to demonstrate how to implement
a Reactor-based HTTP server from scratch in Python.

Core components such as Buffer, HTTP request parser,
and HTTP response builder are implemented manually
to illustrate event-driven network programming.

## Version

**2.2.2**

## install

```shell
pip install reactor-server
```

## example:

```shell
import os

from reactor_server.http_server.eventloop import EventLoop
from reactor_server.http_server.server import Server
from reactor_server.http_server.settings import BASE_DIR

if __name__ == '__main__':
    os.chdir(os.path.join(BASE_DIR))
    Server(loop_cls=EventLoop, thread_num=10).run()
```

## Reactor-based HTTP Server (Python)

- Implemented a non-blocking HTTP server using the Reactor pattern.

- Built custom Buffer, Request parser, and Response builder.

- Implemented static file serving and directory listing.

- Designed multi-reactor architecture with threadpool.

- Handled partial read/write and TCP connection lifecycle.

- Others maybe done in the future?

## Contributions are welcome!
