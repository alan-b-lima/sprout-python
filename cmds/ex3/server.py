from   cmds.ex3  import common
from   internal  import net, tcp
from   pkg       import log, routine
from   pkg.error import Result, Ok, Err
import re
import threading
import queue

def Handle(addr: net.Addr) -> None:
    ln = tcp.Listen(addr)
    if not ln.Ok():
        log.Error(ln.Err())
        return

    ln = ln.Val()

    ip, port = ln.Addr()
    log.Info(f"server listening at {ip}:{port}")

    try:
        users = _Registry()

        while True:
            conn = ln.Accept()
            if not conn.Ok():
                log.Error(conn.Err())
                continue

            routine.Go(_Handler(users, conn.Val()).Handle)

    except KeyboardInterrupt:
        print("\r", end="")

    log.Info("closing server...")
    ln.Close()

class _Registry:
    _users: dict[str, queue.Queue[common.Message]]
    _mu:    threading.Lock

    def __init__(self) -> None:
        self._users = {}
        self._mu    = threading.Lock()

    def Add(self, name: str, queue: queue.Queue[common.Message]) -> bool:
        with self._mu:
            if name in self._users:
                return False
            
            self._users[name] = queue
            return True

    def Remove(self, name: str) -> None:
        with self._mu:
            self._users.pop(name, None)

    def __iter__(self):
        with self._mu:
            return iter(self._users.items())

_reUsername = re.compile("^[0-9A-Za-z\\-]+$")

class _Handler:
    _conn: tcp.Conn
    _head: bytearray
    _buf:  bytearray
    _end:  bool

    _users: _Registry
    _user:  str

    _queue: queue.Queue[common.Message]
    _cond:  threading.Condition

    def __init__(self, users: _Registry, conn: tcp.Conn) -> None:
        self._conn  = conn
        self._head  = bytearray(4)
        self._buf   = bytearray()
        self._end   = False
        self._users = users
        self._user  = ""
        self._queue = queue.Queue()
        self._cond  = threading.Condition()

    def Handle(self) -> None:
        with self._conn:
            ip, port = self._conn.RemoteAddr()
            addr = f"{ip}:{port}"

            log.Info(addr, "connection established")
            self._send(addr)
            log.Info(addr, "connection terminated")

    def _register(self, name: str) -> bool:
        if _reUsername.match(name) is None:
            return False

        if not self._users.Add(name, self._queue):
            return False
        
        self._user = name
        return True

    def _recv(self, addr: str) -> None:
        while not self._conn.Done() and not self._end:
            msg = self._queue.get()

            b = msg.Bytes()
            if not b.Ok():
                log.Error(addr, b.Err())
                return

            err = self._conn.Write(b.Val())
            if not err.Ok():
                log.Error(addr, err.Err())
                return

    def _send(self, addr: str) -> None:
        req = self._recv_req()
        if not req.Ok():
            log.Error(addr, req.Err())
            return
        
        req = req.Val()
        match req:
            case common.Start():
                if self._register(req.Name):
                    log.Info(addr, f"started session with {req.Name}")
                else:
                    log.Error(addr, f"name already taken or invalid: {req.Name}")
                    return

            case _:
                log.Error(addr, "unexpected request")
                return
            
        routine.Go(lambda: self._recv(addr))

        while not self._conn.Done() and not self._end:
            req = self._recv_req()
            if not req.Ok():
                log.Error(addr, req.Err())
                return
            
            req = req.Val()
            match req:
                case common.Message():
                    log.Info(addr, f"received message from {req.Sender}: {req.Content}")
                    self._send_req(req.Content)

                case common.End():
                    log.Info(addr, "received end request")
                    self._end = True

                case _:
                    log.Error(addr, "unexpected request")
                    return

    def _recv_req(self) -> Result[common.Start | common.Message | common.End, Exception]:
        n = self._conn.Read(self._head)
        if not n.Ok():
            return Err(n.Err())

        header = common.HeaderFromBytes(self._head)
        if not header.Ok():
            return Err(header.Err())
        
        header = header.Val()

        if header.Length > len(self._buf):
            self._buf = bytearray(header.Length)

        n = self._conn.Read(self._buf)
        if not n.Ok():
            return Err(n.Err())
            
        req = common.FromBytes(header, self._buf[:n.Val()])
        if not req.Ok():
            return Err(req.Err())

        return Ok(req.Val())

    def _send_req(self, content: str) -> Result[None, Exception]:
        msg = common.Message(self._user, content)

        for name, queue in self._users:
            if name != self._user:
                queue.put(msg)

        return Ok(None)