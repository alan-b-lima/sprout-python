from pkg.error import Result, Ok, Err

def Decode(b: bytes) -> Result[str, None]:
    try:
        return Ok(b.decode("utf-8"))
    except UnicodeDecodeError:
        return Err(None)

def Encode(s: str) -> Result[bytes, None]:
    try:
        return Ok(s.encode("utf-8"))
    except UnicodeEncodeError:
        return Err(None)
