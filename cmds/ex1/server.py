from internal import net, tcp
from pkg      import log, routine, utf8

def Handle(addr: net.Addr) -> None:
    ln = tcp.Listen(addr)
    if not ln.Ok():
        log.Error(ln.Err())
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

    log.Info("closing server...")
    ln.Close()

LF  = b"\012"
ETX = b"\003"

MSG_OK  = b"OK\n"
MSG_BYE = b"BYE\n"

def _handle(conn: tcp.Conn) -> None:
    ip, port = conn.Addr()
    log.Info(f"established connection at {ip}:{port}")

    with conn:
        acc = bytes()

        should_close = False
        while not (conn.Done() or should_close):
            b = conn.Read(4096)
            if not b.Ok():
                log.Error(b.Err())
                break

            err = conn.Write(MSG_OK)
            if not err.Ok():
                log.Error(err.Err())
                break

            b = b.Val()
            index = b.find(ETX)
            if index >= 0:
                acc += b[index:]
                should_close = True
            else:
                acc += b

            while True:
                index = acc.find(LF)
                if index == -1:
                    break

                str = utf8.Decode(acc[:index])
                if not str.Ok():
                    log.Error(f"malformed message from {ip}:{port}")
                    continue

                log.Info(f"message from {ip}:{port}: {str.Val()}")
                acc = acc[index+1:]

        err = conn.Write(MSG_BYE)
        if not err.Ok():
            log.Warn(err.Err())

    log.Info(f"closed connection to {ip}:{port}")
