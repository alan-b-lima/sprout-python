from   internal        import net
from   pkg             import routine
from   pkg.error       import Result, Ok, Err
import sys
import threading
from   websockets      import WebSocketException
from   websockets.sync import client

def Handle(addr: net.Addr, name: str):
    host, port = addr
    uri = f"ws://{host}:{port}/{name}"

    try:
        conn = client.connect(uri)
        with conn:
            try:
                conn.ping()
            except WebSocketException as ex:
                print(f"ping: {ex}")
                return

            print(f"connection established to {uri}")
            _Handler(conn).Run()

    except KeyboardInterrupt:
        print("\r", end="") 

class _Handler:
    _conn: client.ClientConnection
    _skip: int
    _mu:   threading.Lock

    def __init__(self, conn: client.ClientConnection) -> None:
        self._conn = conn
        self._skip = 0
        self._mu   = threading.Lock()

    def Run(self) -> None:
        routine.Go(self._recv)
        self._send()

    def _recv(self) -> Result[None, WebSocketException]:
        while True:
            try:
                msg = self._conn.recv(decode=True)
            except WebSocketException as ex:
                return Err(ex)

            name, time, content = msg.split(";", 2)
            
            with self._mu:
                self._skip += 1
                skip = self._skip

            sys.stdout.write("\033[s" + "\n" * skip + f"[{name}] {time}: {content}\033[u")
            sys.stdout.flush()

    def _send(self) -> Result[None, WebSocketException]:
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

            try:
                self._conn.send(str, text=True)
            except WebSocketException as ex:
                print("connection error")
                return Err(ex)
