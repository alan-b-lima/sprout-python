from   pkg.error import error
import threading
from   typing    import Callable

def Go(func: Callable[[], None]) -> None:
    if not callable(func):
        raise error("not callable")

    thread = threading.Thread(None, func, daemon=True)
    thread.start()
