import socket
from   pkg.error import Result, Ok, Err, error

type Addr = tuple[str, int]

def ParseAddr(str: str) -> Result[Addr, Exception]:
    secs = str.rsplit(":", 1)
    if len(secs) != 2:
        return Err(error("net: malformed address"))
    
    ip, port_str = secs

    if ip == "":
        ip = "0.0.0.0"

    if port_str != "":
        try:
            port = int(port_str)
        except ValueError as ex:
            return Err(error("net: malformed address", ex))
        if port < 0 or port > 65535:
            return Err(error("net: malformed address: port out of range"))
    else:
        port = 0

    return Ok((ip, port))

def Shutdown(sock: socket.socket) -> Exception | None:
    try:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    except OSError as ex:
        return ex
