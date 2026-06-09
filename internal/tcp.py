import socket
import threading
from pkg.error import Result, Ok, Err, error

type addr = tuple[str, int]

class Conn:
    _addr: addr
    _sock: socket.socket

    _wait: bool
    _done: bool
    _mu: threading.Lock

    def __init__(self, sock: socket.socket, addr: addr) -> None:
        self._addr = addr
        self._sock = sock
        self._wait = False
        self._done = False
        self._mu = threading.Lock()

    def Read(self, n: int) -> Result[bytes, Exception]:
        with self._mu:
            self._wait = True

        try:
            return Ok(self._sock.recv(n))
        except OSError as ex:
            return Err(error("conn read", ex))
        finally:
            with self._mu:
                self._wait = False

    def Write(self, data: bytes) -> Result[int, Exception]:
        with self._mu:
            self._wait = False

        try:
            return Ok(self._sock.send(data))
        except OSError as ex:
            return Err(error("conn aborted", ex))
        finally:
            with self._mu:
                self._wait = False

    def Addr(self) -> addr:
        return self._addr

    def Close(self) -> Result[None, Exception]:
        with self._mu:
            if self._done == True:
                return Ok(None)

            self._done = True

        try:
            with self._mu:
                if self._wait == True:
                    self._sock.shutdown(socket.SHUT_RDWR)            

            self._sock.close()
            return Ok(None)

        except OSError as ex:
            return Err(error("conn close", ex))

    def Done(self) -> bool:
        with self._mu:
            return self._done

class Listener:
    _addr: addr
    _sock: socket.socket

    _conns: list[Conn]
    _done: bool
    _mu: threading.Lock

    def __init__(self, fd: socket.socket, addr: addr) -> None:
        self._addr = addr
        self._sock = fd
        self._conns = []
        self._done = False
        self._mu = threading.Lock()

    def Accept(self) -> Result[Conn, Exception]:
        try:
            sock, addr = self._sock.accept()
            conn = Conn(sock, addr)
            with self._mu:
                self._conns.append(conn)

            return Ok(conn)

        except OSError as ex:
            return Err(error("accept", ex))

    def Addr(self) -> addr:
        return self._addr

    def Close(self) -> None:
        with self._mu:
            if self._done == True:
                return

            self._done = True
            for conn in self._conns:
                conn.Close()

        self._sock.close()

    def Done(self) -> bool:
        with self._mu:
            return self._done

def Dial(addr: addr) -> Result[Conn, Exception]:
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.connect(addr)

    except OSError as ex:
        ip, port = addr
        return Err(error(f"dial at {ip}:{port}", ex))
    
    return Ok(Conn(fd, addr))

def Listen(addr: addr) -> Result[Listener, Exception]:
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.bind(addr)
        fd.listen(1)

    except OSError as ex:
        ip, port = addr
        return Err(error(f"listen to {ip}:{port}", ex))
    
    return Ok(Listener(fd, addr))