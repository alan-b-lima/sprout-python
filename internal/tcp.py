from   internal  import net
from   pkg.error import Result, Ok, Err, error
import socket
import threading

class Conn:
    _laddr: net.Addr
    _raddr: net.Addr
    _sock:  socket.socket

    _done: bool
    _mu:   threading.Lock

    def __init__(self, sock: socket.socket) -> None:
        self._laddr = sock.getsockname()
        self._raddr = sock.getpeername()

        self._sock = sock
        self._done = False
        self._mu   = threading.Lock()

    def Read(self, data: bytearray) -> Result[int, Exception]:
        try:
            return Ok(self._sock.recv_into(data))

        except OSError as ex:
            return Err(error("conn read", ex))

    def Write(self, data: bytes) -> Result[int, Exception]:
        try:
            return Ok(self._sock.send(data))

        except OSError as ex:
            return Err(error("conn aborted", ex))

    def LocalAddr(self) -> net.Addr:
        return self._laddr

    def RemoteAddr(self) -> net.Addr:
        return self._raddr

    def Close(self) -> None:
        with self._mu:
            if self._done == True:
                return
            self._done = True

        net.Shutdown(self._sock)

    def Done(self) -> bool:
        with self._mu:
            return self._done

    def __enter__(self):
        pass

    def __exit__(self, ex_t: object, ex_v: object, tb: object):
        self.Close()

class Listener:
    _addr: net.Addr
    _sock: socket.socket

    _conns: list[Conn]
    _done:  bool
    _mu:    threading.Lock

    def __init__(self, sock: socket.socket) -> None:
        self._addr  = sock.getsockname()
        self._sock  = sock
        self._conns = []
        self._done  = False
        self._mu    = threading.Lock()

    def Accept(self) -> Result[Conn, Exception]:
        try:
            sock, _ = self._sock.accept()
            conn = Conn(sock)
            self._add(conn)
            return Ok(conn)

        except OSError as ex:
            return Err(error("accept", ex))

    def Addr(self) -> net.Addr:
        return self._addr

    def Close(self) -> None:
        net.Shutdown(self._sock)

        with self._mu:
            if self._done == True:
                return

            self._done = True
            for conn in self._conns:
                conn.Close()

    def Done(self) -> bool:
        with self._mu:
            return self._done

    def _add(self, conn: Conn) -> None:
        with self._mu:
            i = 0
            for c in self._conns:
                if c.Done():
                    self._conns[i] = c
                    i += 1

            self._conns = self._conns[:i]
            self._conns.append(conn)

    def __enter__(self):
        pass

    def __exit__(self, ex_t: object, ex_v: object, tb: object):
        self.Close()

def Dial(addr: net.Addr) -> Result[Conn, Exception]:
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.connect(addr)

    except OSError as ex:
        ip, port = addr
        return Err(error(f"dial at {ip}:{port}", ex))
    
    return Ok(Conn(fd))

def Listen(addr: net.Addr) -> Result[Listener, Exception]:
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.bind(addr)
        fd.listen(1)

    except OSError as ex:
        ip, port = addr
        return Err(error(f"listen to {ip}:{port}", ex))
    
    return Ok(Listener(fd))