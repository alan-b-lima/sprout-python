from internal  import net, tcp
from pkg       import log, routine, utf8
from pkg.error import Result, Ok, Err, error

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

            routine.Go(Handler(conn.Val()))

    except KeyboardInterrupt:
        print("\r", end="")

    log.Info("closing server...")
    ln.Close()

LF  = b"\012"
ETX = b"\003"

MSG_OK  = b"OK\n"
MSG_BYE = b"BYE\n"

class Handler:
    _conn: tcp.Conn

    _acc: bytearray
    _buf: bytearray
    _etx: bool

    def __init__(self, conn: tcp.Conn) -> None:
        self._conn = conn
        self._acc  = bytearray()
        self._buf  = bytearray(4096)
        self._etx  = False

    def __call__(self) -> None:
        with self._conn:
            ip, port = self._conn.RemoteAddr()
            addr = f"{ip}:{port}"

            log.Info(addr, "connection established")
            self._handle(addr)
            log.Info(addr, "connection terminated")

    def _handle(self, addr: str) -> None:
        while not self._conn.Done() and not self._etx:
            line = self._read_line()
            if not line.Ok():
                log.Error(line.Err())
                break

            if self._etx:
                log.Info(addr, "received end of text")
                err = self._conn.Write(MSG_BYE)
            else:
                err = self._conn.Write(MSG_OK)

            if not err.Ok():
                log.Error(addr, err.Err())
                break

            line = line.Val()
            if len(line) == 0:
                continue

            log.Info(addr, f"message: {line}")

    def _read_line(self) -> Result[str, Exception]:
        index = self._find(self._acc)
        if index != -1:
            line, self._acc = self._acc[:index], self._acc[index+1:]
            return self._encode(line)

        while True:
            n = self._conn.Read(self._buf)
            if not n.Ok():
                return Err(n.Err())
            
            n = n.Val()
            buf = self._buf[:n]

            index = self._find(buf)
            if index != 1:
                line = self._acc + buf[:index]
                self._acc = bytearray(buf[index+1:])

                return self._encode(line)
    
            self._acc += buf

    def _find(self, buf: bytes) -> int:
        for i, byte in enumerate(buf):
            if byte in LF:
                return i

            if byte in ETX:
                self._etx = True
                return i

        return -1
    
    def _encode(self, line: bytes) -> Result[str, Exception]:
        str = utf8.Decode(line)
        if not str.Ok():
            return Err(error(f"malformed message"))
        
        return Ok(str.Val())
