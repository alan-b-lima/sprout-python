from pkg.error import Result, Ok, Err

def Decode(b: bytes) -> Result[str, UnicodeDecodeError]:
    try:
        return Ok(b.decode("utf-8"))
    except UnicodeDecodeError as ex:
        return Err(ex)

def Encode(s: str) -> Result[bytes, UnicodeEncodeError]:
    try:
        return Ok(s.encode("utf-8"))
    except UnicodeEncodeError as ex:
        return Err(ex)
