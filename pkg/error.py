class Result[T, E]:
    def Ok(self) -> bool:
        raise

    def Val(self) -> T:
        raise

    def Err(self) -> E:
        raise

    def Unwrap(self) -> T:
        if self.Ok():
            return self.Val()

        err = self.Err()
        if isinstance(err, BaseException):
            raise err
        
        raise Exception(err)

class Ok[T, E](Result[T, E]):
    val: T

    def __init__(self, val: T):
        super().__init__()
        self.val = val

    def Ok(self) -> bool:
        return True
    
    def Val(self) -> T:
        return self.val

class Err[T, E](Result[T, E]):
    err: E

    def __init__(self, err: E):
        super().__init__()
        self.err = err

    def Ok(self) -> bool:
        return False

    def Err(self) -> E:
        return self.err

class error(Exception):
    _msg: str
    _ex: BaseException | None

    def __init__(self, msg: str, ex: BaseException | None = None) -> None:
        self._msg = msg
        self._ex = ex

    def __str__(self) -> str:
        if self._ex is None:
            return self._msg
        return self._msg + ": " + str(self._ex)
