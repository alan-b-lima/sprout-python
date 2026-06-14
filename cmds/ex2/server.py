from typing import Callable

from internal import net, udp
from pkg      import log, routine

KiB = 1024

def Handle(addr: net.Addr) -> None:
    ln = udp.Listen(addr)
    if not ln.Ok():
        log.Error(ln.Err())
        return
    
    ln = ln.Val()

    ip, port = ln.Addr()
    log.Info(f"server listening at {ip}:{port}")

    pool = routine.Pool(4)

    try:
        while True:
            buf = bytearray(64*KiB)

            d = ln.ReadFrom(buf)
            if not d.Ok():
                log.Error(d.Err())
                continue

            n, addr = d.Val()
            pool.Go(_handler(ln, addr, buf[:n]))

    except KeyboardInterrupt:
        print("\r", end="")

    log.Info("closing server...")

    pool.Close()
    ln.Close()

def _handler(ln: udp.Listener, addr: net.Addr, buf: bytes) -> Callable[[], None]:
    def handle() -> None:
        err = ln.WriteTo(buf, addr)
        if not err.Ok():
            log.Error(err.Err())
            return

        ip, port = addr
        log.Info(f"{ip}:{port}", "echo")

    return handle