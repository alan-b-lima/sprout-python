from internal  import net, tcp
from pkg       import utf8
from pkg.error import Result, Ok, Err, error

def Handle(addr: net.Addr) -> None:
    conn = tcp.Dial(addr)
    if not conn.Ok():
        print(f"error: {conn.Err()}")
        return

    conn = conn.Val()

    ip, port = conn.Addr()
    print(f"connection listening at {ip}:{port}")

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

                res = read(conn, "OK\n")
                if not res.Ok():
                    print(f"error: {res.Err()}")
                    break
        
                print("sent!")

        except KeyboardInterrupt:
            print("\r", end="")
            err = conn.Write(b"\003")
            if not err.Ok():
                print(f"write: {err.Err()}")
                return

def read(conn: tcp.Conn, sentinel: str) -> Result[None, Exception]:
    b = conn.Read(len(sentinel))
    if not b.Ok():
        return Err(b.Err())

    msg = utf8.Decode(b.Val())
    if not msg.Ok() or msg.Val() != sentinel:
        return Err(error("malformed response"))

    return Ok(None)
