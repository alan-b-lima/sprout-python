import queue
import threading
from   typing import Any, Callable

def Go(func: Callable[[], Any]) -> None:
    if not callable(func):
        raise ValueError("not callable")

    thread = threading.Thread(None, func, daemon=True)
    thread.start()

class Pool:
    _cond: threading.Condition
    _work: queue.Queue[Callable[[], None]]

    def __init__(self, workers: int) -> None:
        self._cond = threading.Condition()
        self._work = queue.Queue(workers)
        self._open = True

        for _ in range(workers):
            Go(self._routine)

    def Go(self, func: Callable[[], None]) -> None:
        with self._cond:
            while self._work.full():
                self._cond.wait()
            
            self._work.put(func)
            self._cond.notify()

    def Close(self) -> None:
        self._open = False

    def _routine(self) -> None:
        while self._open:
            with self._cond:
                while self._work.empty():
                    self._cond.wait()
                
                func = self._work.get()
    
                func()
                self._cond.notify()
