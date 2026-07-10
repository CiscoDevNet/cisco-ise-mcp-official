from enum import Enum

class LinkRel(str, Enum):
    NEXT = "next"
    PREVIOUS = "previous"
    SELF = "self"
    STATUS = "status"

    def __str__(self) -> str:
        return str(self.value)
