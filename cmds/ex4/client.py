from internal import net, tcp
from pkg      import utf8

def Handle(addr: net.Addr) -> None:
    conn = tcp.Dial(addr)
    if not conn.Ok():
        print(conn.Err())
        return

    conn = conn.Val()
    buf = bytearray(1024)

    with conn:
        n = conn.Read(buf)
        if not n.Ok():
            print(f"error: {n.Err()}")
            return

        n = n.Val()
        text = utf8.Decode(buf[:n])
        if not text.Ok():
            print(f"error: malformed response")
            return

        ip, port = conn.RemoteAddr()
        print(f"time from {ip}:{port}: {text.Val()}")
