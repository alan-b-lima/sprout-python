from   internal  import net
from   pkg.error import Result, Ok, Err, error
import socket

class Listener:
    _addr: net.Addr
    _sock: socket.socket
    
    def __init__(self, sock: socket.socket) -> None:
        self._addr = sock.getsockname()
        self._sock = sock

    def ReadFrom(self, data: bytearray) -> Result[tuple[int, net.Addr], Exception]:
        try:
            n, addr = self._sock.recvfrom_into(data, len(data))
            return Ok((n, addr))

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
        net.Shutdown(self._sock)

    def __enter__(self):
        pass

    def __exit__(self, ex_t: object, ex_v: object, tb: object):
        self.Close()

def Listen(addr: net.Addr) -> Result[Listener, Exception]:
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fd.bind(addr)

        return Ok(Listener(fd))

    except OSError as ex:
        return Err(error("listener", ex))
