from   internal  import net
from   pkg.error import Result, Ok, Err, error
import socket

class Listener:
    _addr: net.Addr
    _sock: socket.socket
    
    def __init__(self, addr: net.Addr) -> None:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.bind(addr)

        self._addr = addr
        self._sock = fd

    def ReadFrom(self, n: int) -> Result[tuple[bytes, net.Addr], Exception]:
        try:
            bytes, addr = self._sock.recvfrom(n)
            return Ok((bytes, addr))

        except OSError as ex:
            return Err(error("read from", ex))

    def WriteTo(self, b: bytes, addr: net.Addr) -> Result[int, Exception]:
        try:
            return Ok(self._sock.sendto(b, addr))

        except OSError as ex:
            return Err(error("write to", ex))

    def Addr(self) -> net.Addr:
        return self._addr

    def Close(self) -> None:
        self._sock.close()

def Listen(addr: net.Addr) -> Result[Listener, Exception]:
    try:
        return Ok(Listener(addr))

    except OSError as ex:
        return Err(error("listener", ex))
