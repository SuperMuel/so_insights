from enum import Enum


class TimeLimit(str, Enum):
    D = "d"
    M = "m"
    W = "w"
    Y = "y"

    def __str__(self) -> str:
        return str(self.value)
