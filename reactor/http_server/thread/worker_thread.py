import threading

from reactor.http_server.eventloop import EventLoop


class WorkerThread:
    def __init__(self, index_in_pool: int | None = None):
        self._index_in_pool = index_in_pool
        self._name = f'SubThread-{index_in_pool}'
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._mutex = threading.RLock()
        self._condition = threading.Condition()
        self._loop: EventLoop | None = None

    def run(self):
        self._thread = threading.Thread(target=self._target)
        self._thread.start()

        with self._condition:
            while self._loop is None:
                self._condition.wait()

    def _target(self):
        self._thread_id = threading.get_ident()

        with self._condition:
            self._loop = EventLoop(thread_name=self._name)
            self._condition.notify()
        self._loop.run()

    @property
    def loop(self):
        return self._loop
