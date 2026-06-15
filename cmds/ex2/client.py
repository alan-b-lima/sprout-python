from internal  import net, udp
from pkg       import bits, utf8
from pkg.error import Result, Ok, Err

def Handle(addr: net.Addr) -> None:
    conn = udp.Dial(addr)
    if not conn.Ok():
        print(f"error: {conn.Err()}")
        return

    conn = conn.Val()

    lip, lport = conn.LocalAddr()
    rip, rport = conn.RemoteAddr()

    print(f"client started at {lip}:{lport} to {rip}:{rport}")

    buf = bytearray()

    try:
        while True:
            str = input("> ").strip()
            if str == "/exit":
                break

            if len(str) == 0:
                continue

            b = _tobytes(str)
            if not b.Ok():
                print(f"error: {b.Err()}")
                continue

            b = b.Val()
            err = conn.Write(b)
            if not err.Ok():
                print(f"error: {err.Err()}")
                continue

            if len(b) > len(buf):
                buf = bytearray(len(b))

            n = conn.Read(buf)
            if not n.Ok():
                print(f"error: {n.Err()}")
                continue

            str = utf8.Decode(buf[:n.Val()])
            if not str.Ok():
                print("malformed response")

            print(str.Val())

    except KeyboardInterrupt:
        print("\r", end="")

    conn.Close()

def _tobytes(s: str) -> Result[bytes, Exception]:
    if len(s) > 64*bits.KiB:
        return Err(ValueError("message too long"))

    b = utf8.Encode(s)
    if not b.Ok():
        return Err(ValueError("malformed string"))
    
    b = b.Val()
    if len(b) > 64*bits.KiB:
        return Err(ValueError("message too long"))

    return Ok(b)
