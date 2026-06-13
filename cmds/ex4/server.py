from datetime import datetime
from internal import net, tcp
from pkg      import log, routine, utf8

def Handle(addr: net.Addr) -> None:
    ln = tcp.Listen(addr)
    if not ln.Ok():
        log.Error(f"{ln.Err()}")
        return

    ln = ln.Val()

    ip, port = ln.Addr()
    log.Info(f"server listening at {ip}:{port}")

    try:
        while True:
            conn = ln.Accept()
            if not conn.Ok():
                log.Error(conn.Err())
                continue

            routine.Go(lambda: _handle(conn.Val()))

    except KeyboardInterrupt:
        print("\r", end="")

    log.Info(f"closing server...")
    ln.Close()

def _handle(conn: tcp.Conn) -> None:
    with conn:
        now = datetime.now()

        time = now.strftime("%H:%M:%S")
        b = utf8.Encode(time).Unwrap()

        err = conn.Write(b)
        if not err.Ok():
            log.Error(err.Err())
            return

        ip, port = conn.RemoteAddr()
        log.Info(f"{ip}:{port}", "request", time)
