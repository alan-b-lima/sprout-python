def Decode(b: bytes) -> tuple[str, bool]:
    try:
        return b.decode("utf-8"), True
    except UnicodeDecodeError:
        return "", False

def Encode(s: str) -> tuple[bytes, bool]:
    try:
        return s.encode("utf-8"), True
    except UnicodeEncodeError:
        return bytes(), False
