from   cmds.ex3  import common
from   internal  import net, tcp
from   pkg       import bits, routine
from   pkg.error import Result, Ok, Err
import sys
import threading

def Handle(addr: net.Addr, name: str):
    conn = tcp.Dial(addr)
    if not conn.Ok():
        print(f"error: {conn.Err()}")
        return

    conn = conn.Val()

    lip, lport = conn.LocalAddr()
    rip, rport = conn.RemoteAddr()

    print(f"connection established to {rip}:{rport} from {lip}:{lport}")

    try:
        with conn:
            _Handler(name, conn).Run()

    except KeyboardInterrupt:
        print("\r", end="")

    print("bye!")

class _Handler:
    _name: str
    _conn: tcp.Conn
    _skip: int
    _mu:   threading.Lock

    def __init__(self, name: str, conn: tcp.Conn) -> None:
        self._name = name
        self._conn = conn
        self._skip = 0
        self._mu   = threading.Lock()

    def Run(self) -> None:
        req = common.Start(self._name)
        res = req.Bytes()
        if not res.Ok():
            print(f"error: {res.Err()}")
            return
        
        err = self._conn.Write(res.Val())
        if not err.Ok():
            print(f"write: {err.Err()}")
            return

        routine.Go(self._recv)
        
        err = self._send()
        if not err.Ok():
            print(err.Err())

        req = common.End()
        res = req.Bytes()
        if not res.Ok():
            print(f"error: {res.Err()}")
            return
        
        data = res.Val()
        err = self._conn.Write(data)
        if not err.Ok():
            print(f"write: {err.Err()}")

    def _start(self) -> Result[None, Exception]:
        req = common.Start(self._name)
        res = req.Bytes()
        if not res.Ok():
            return Err(res.Err())

        data = res.Val()
        err = self._conn.Write(data)
        if not err.Ok():
            print(f"write: {err.Err()}")
            return Err(err.Err())
        
        return Ok(None)

    def _send(self) -> Result[None, Exception]:
        while True:
            with self._mu:
                if self._skip > 0:
                    print("\n" * self._skip, end="")
                    self._skip = 0

            str = input("> ").strip()
            if str == "/exit":
                return Ok(None)

            if len(str) == 0:
                continue

            msg = common.Message(self._name, str)

            data = msg.Bytes()
            if not data.Ok():
                print(f"message: {data.Err()}")
                continue

            err = self._conn.Write(data.Val())
            if not err.Ok():
                print(f"write: {err.Err()}")
                return Err(err.Err())

    def _recv(self) -> Result[None, Exception]:
        head = bytearray(4)
        body = bytearray()
        
        while True:
            err = self._conn.Read(head)
            if not err.Ok():
                return Err(Exception("read", err.Err()))

            header = common.HeaderFromBytes(head[:err.Val()])
            if not header.Ok():
                return Err(Exception("header", header.Err()))
            
            header = header.Val()
            if header.Length >= 64*bits.KiB:
                return Err(Exception("message too big"))
            
            if len(body) < header.Length:
                body = bytearray(header.Length)

            n = self._conn.Read(body)
            if not n.Ok():
                return Err(Exception("read", n.Err()))
            
            if n.Val() != header.Length:
                return Err(Exception("unexpected message length"))
            
            if header.Kind != common.RequestKind.Message:
                return Err(Exception("unexpected request kind"))
            
            if len(body) == 0:
                continue

            msg = common.Message()
            msg.FromBytes(body)

            with self._mu:
                self._skip += 1
                skip = self._skip

            sys.stdout.write("\033[s" + "\n" * skip + f"[{msg.Sender}] {msg.Time}: {msg.Content}\033[u")
            sys.stdout.flush()
