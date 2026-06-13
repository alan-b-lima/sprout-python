from internal import net, tcp
from pkg      import log, utf8

def Handle(addr: net.Addr) -> None:
    conn = tcp.Dial(addr)
    if not conn.Ok():
        log.Error(f"{conn.Err()}")
        return

    conn = conn.Val()
    buf = bytearray(1024)

    with conn:
        n = conn.Read(buf)
        if not n.Ok():
            log.Error(n.Err())
            return

        n = n.Val()
        text = utf8.Decode(buf[:n])
        if not text.Ok():
            log.Error("malformed response")
            return

        ip, port = conn.RemoteAddr()
        log.Info(f"{ip}:{port}", text.Val())
