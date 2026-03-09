import inspect
import threading

from http_server.eventloop import EventLoop
from http_server.thread.worker_thread import WorkerThread


class ThreadPool:
    def __init__(self, loop: EventLoop, thread_num: int):
        self._loop = loop
        self._thread_num = thread_num
        self._is_start = False
        self._workers: list[WorkerThread] = []
        self._index = 0

    def run(self):
        self._check_runtime()
        self._is_start = True
        if self._thread_num > 0:
            for index in range(self._thread_num):
                sub_thread = WorkerThread(index_in_pool=index)
                sub_thread.run()
                self._workers.append(sub_thread)

    def take_worker(self):
        # self._check_runtime()
        loop = self._loop
        if self._thread_num > 0:
            loop = self._workers[self._index].loop
            self._index += 1
            self._index %= self._thread_num
        return loop

    def _check_runtime(self):
        if self._is_start:
            frame = inspect.stack()[0]
            raise RuntimeError(f'ThreadPool has already started, line: {frame.lineno}, func: {frame.function}')
        # if self._loop.thread_id != threading.get_ident():
        if self._loop.thread_id is not None and self._loop.thread_id != threading.get_ident():
            frame = inspect.stack()[0]
            raise RuntimeError(f'loop id error, line: {frame.lineno}, func: {frame.function}')
