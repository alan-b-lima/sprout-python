from internal  import net, tcp
from pkg       import utf8
from pkg.error import Result, Ok, Err, error

def Handle(addr: net.Addr) -> None:
    conn = tcp.Dial(addr)
    if not conn.Ok():
        print(f"error: {conn.Err()}")
        return

    conn = conn.Val()

    lip, lport = conn.LocalAddr()
    rip, rport = conn.RemoteAddr()

    print(f"connection established to {rip}:{rport} from {lip}:{lport}")

    with conn:
        try:
            while True:
                str = input("> ").strip()
                if str == "/exit":
                    break

                if len(str) == 0:
                    continue

                b = utf8.Encode(str + "\n")
                if not b.Ok():
                    print("error: malformed message")
                    continue

                err = conn.Write(b.Val())
                if not err.Ok():
                    print(f"write: {err.Err()}")
                    break

                res = _read(conn, "OK\n")
                if not res.Ok():
                    print(f"read: {res.Err()}")
                    break
        
                print("sent!")

        except KeyboardInterrupt:
            print("\r", end="")
            
        err = conn.Write(b"\003")
        if not err.Ok():
            print(f"write: {err.Err()}")
            return

        res = _read(conn, "BYE\n")
        if not res.Ok():
            print(f"read: {res.Err()}")
            return

        print("bye!")

def _read(conn: tcp.Conn, sentinel: str) -> Result[None, Exception]:
    b = bytearray(len(sentinel))

    err = conn.Read(b)
    if not err.Ok():
        return Err(err.Err())

    msg = utf8.Decode(b)
    if not msg.Ok() or msg.Val() != sentinel:
        return Err(error("malformed response"))

    return Ok(None)
