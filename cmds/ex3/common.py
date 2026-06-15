from datetime  import datetime
from enum      import Enum
from pkg       import bits, utf8
from pkg.error import Result, Ok, Err, error

Version: int = 1

class RequestKind(Enum):
    Start   = 1
    Message = 2
    End     = 4

class Header:
    Kind:    RequestKind
    Length:  int

    def __init__(self, kind: RequestKind, length: int) -> None:
        self.Kind    = kind
        self.Length  = length

    def PutBytes(self, data: bytearray) -> None:
        if len(data) < 4:
            raise ValueError("data too small")

        data[0] = Version
        data[1] = self.Kind.value
        
        if self.Length < 0 or self.Length >= 64*bits.KiB:
            raise ValueError(f"{self.Length} out of range for uint16")

        data[2] = (self.Length >> 0x00) & 0xFF
        data[3] = (self.Length >> 0x08) & 0xFF

def HeaderFromBytes(data: bytes) -> Result[Header, Exception]:
    if len(data) < 4:
        return Err(error("data too small"))

    version = data[0]
    if version != Version:
        return Err(ValueError("unknown version"))

    return Ok(Header(
        RequestKind(data[1]), 
        (data[2] << 0x00) | (data[3] << 0x08)
    ))

class Start:
    Name: str
    
    def __init__(self, name: str) -> None:
        self.Name = name

    def Bytes(self) -> Result[bytes, Exception]:
        b = utf8.Encode(self.Name)
        if not b.Ok():
            return Err(b.Err())

        b = b.Val()
        if len(b) >= 64*bits.KiB:
            return Err(error("too big"))

        data = bytearray(4 + len(b))

        header = Header(RequestKind.Start, len(b))
        header.PutBytes(data)

        data[4:] = b
        return Ok(data)

class Message:
    Sender:  str
    Content: str
    Time:    datetime

    def __init__(self, sender: str = "", content: str = "") -> None:
        self.Sender  = sender
        self.Content = content
        self.Time    = datetime.now()

    def Bytes(self) -> Result[bytes, Exception]:
        b = utf8.Encode(f"{self.Sender} {self.Time.isoformat("T", "seconds")} {self.Content}")
        if not b.Ok():
            return Err(b.Err())

        b = b.Val()
        if len(b) >= 64*bits.KiB:
            return Err(error("too big"))

        data = bytearray(4 + len(b))
        
        header = Header(RequestKind.Message, len(b))
        header.PutBytes(data)
        
        data[4:] = b
        return Ok(data)

    def FromBytes(self, data: bytes) -> Result[None, Exception]:
        str = utf8.Decode(data)
        if not str.Ok():
            return Err(str.Err())

        splits = str.Val().split(" ", 2)
        if len(splits) != 3:
            return Err(error("invalid message format"))

        sender, time, content = splits

        self.Sender  = sender
        self.Content = content        
        self.Time    = datetime.fromisoformat(time)

        return Ok(None)

class End:
    def Bytes(self) -> Result[bytes, Exception]:
        data = bytearray(4)

        header = Header(RequestKind.End, 0)
        header.PutBytes(data)

        return Ok(data)

def FromBytes(header: Header, body: bytes) -> Result[Start | Message | End, Exception]:
    match header.Kind:
        case RequestKind.Start:
            str = utf8.Decode(body)
            if not str.Ok():
                return Err(str.Err())

            return Ok(Start(str.Val()))

        case RequestKind.Message:
            msg = Message()
            res = msg.FromBytes(body)
            if not res.Ok():
                return Err(res.Err())

            return Ok(msg)

        case RequestKind.End:
            return Ok(End())

    return Err(error("invalid request kind"))
