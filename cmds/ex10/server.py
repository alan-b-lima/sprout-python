import asyncio
from   datetime           import datetime
from   internal           import net
from   pkg                import log
from   pkg.error          import Result, Ok, Err
import re
from   websockets         import WebSocketException
from   websockets.asyncio import server

from pkg.error import Result

def Handle(addr: net.Addr):
    async def handle(addr: net.Addr) -> None:
        handler = _Handler()
        host, port = addr

        s = await server.serve(handler.Handle, host, port)

        async with s:
            log.Info(f"server listening at ws://{host}:{port}")
            await s.serve_forever()

    try:
        asyncio.run(handle(addr))
    except KeyboardInterrupt:
        print("\r", end="")
    
    log.Info("closing server...")

_reUsername = re.compile("^[0-9A-Za-z\\-]+$")

class _Message:
    User:    str
    Time:    datetime
    Content: str

    def __init__(self, user: str, content: str) -> None:
        self.User    = user
        self.Time    = datetime.now()
        self.Content = content

    def __str__(self) -> str:
        return f"{self.User};{self.Time.isoformat()};{self.Content}"

class _User:
    Name:  str
    Queue: asyncio.Queue[_Message]
    _conn:  server.ServerConnection

    def __init__(self, name: str, conn: server.ServerConnection) -> None:
        self.Name  = name
        self.Queue = asyncio.Queue()
        self._conn = conn
    
    async def Recv(self) -> Result[str, WebSocketException]:
        try:
            return Ok(await self._conn.recv(decode=True))
        except WebSocketException as ex:
            return Err(ex)

    async def Send(self, data: str) -> Result[None, WebSocketException]:
        try:
            return Ok(await self._conn.send(data, text=True))
        except WebSocketException as ex:
            return Err(ex)

class _Handler:
    _users: dict[str, _User]
    _mu:    asyncio.Lock

    def __init__(self) -> None:
        self._users = {}
        self._mu    = asyncio.Lock()

    async def Handle(self, conn: server.ServerConnection) -> None:
        async with conn:
            host, port = conn.remote_address
            addr = f"{host}:{port}"

            if conn.request is None:
                log.Error(addr, "malformed path")
                return

            path = conn.request.path
            if len(path) == 0 or path[0] != "/":
                log.Error(addr, "malformed path")
                return
            
            name = path[1:]
            if _reUsername.match(name) is None:
                log.Error(addr, "invalid name", name)
                return

            try:
                async with self._mu:
                    if name in self._users:
                        log.Error(addr, "name already taken", name)
                        return

                    user = _User(name, conn)
                    self._users[name.lower()] = user

                log.Info(addr, f"connection established with {name}")
                await asyncio.gather(
                    self._recv(user),
                    self._send(user),
                )

            finally:
                async with self._mu:
                    self._users.pop(name, None)
    
    async def _recv(self, user: _User) -> None:
        while True:
            msg = await user.Queue.get()

            err = await user.Send(str(msg))
            if not err.Ok():
                log.Error(err.Err())
                return

    async def _send(self, user: _User) -> None:
        while True:
            data = await user.Recv()
            if not data.Ok():
                log.Error(data.Err())
                return

            msg = _Message(user.Name, data.Val())

            async with self._mu:
                for u in self._users.values():
                    if u != user:
                        log.Info(user.Name, "messages", u.Name)
                        await u.Queue.put(msg)
