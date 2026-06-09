import threading
from typing import Callable
from pkg.error import error

def Go(func: Callable[[], None]) -> None:
    if not callable(func):
        raise error("not callable")

    thread = threading.Thread(None, func, daemon=True)
    thread.start()
