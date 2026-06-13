from datetime import datetime
from enum     import Enum, auto

class Level(Enum):
    Info  = auto()
    Warn  = auto()
    Error = auto()

    def __str__(self) -> str:
        match self:
            case Level.Info:
                return "INFO"
            case Level.Warn:
                return "WARN"
            case Level.Error:
                return "ERROR"

def Log(level: Level, *values: object) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(stamp, level, *values)

def Info(*values: object) -> None:
    Log(Level.Info, *values)

def Warn(*values: object) -> None:
    Log(Level.Warn, *values)

def Error(*values: object) -> None:
    Log(Level.Error, *values)
