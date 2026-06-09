import socket
from pkg.error import Result, Ok, Err, error

addr = tuple[str, int]

class Listener:
    _addr: addr
    _sock: socket.socket
    
    def __init__(self, addr: addr) -> None:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.bind(addr)

        self._addr = addr
        self._sock = fd

    def ReadFrom(self, n: int) -> Result[tuple[bytes, addr], Exception]:
        try:
            bytes, addr = self._sock.recvfrom(n)
            return Ok((bytes, addr))

        except OSError as ex:
            return Err(error("read from", ex))

    def WriteTo(self, b: bytes, addr: addr) -> Result[int, Exception]:
        try:
            return Ok(self._sock.sendto(b, addr))

        except OSError as ex:
            return Err(error("write to", ex))

    def Addr(self) -> addr:
        return self._addr

    def Close(self) -> None:
        self._sock.close()

def Listen(addr: addr) -> Result[Listener, Exception]:
    try:
        return Ok(Listener(addr))

    except OSError as ex:
        return Err(error("listener", ex))
