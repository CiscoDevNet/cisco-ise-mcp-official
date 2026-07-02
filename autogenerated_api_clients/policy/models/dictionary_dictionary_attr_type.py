from enum import Enum

class DictionaryDictionaryAttrType(str, Enum):
    ENTITY_ATTR = "ENTITY_ATTR"
    MSG_ATTR = "MSG_ATTR"
    PIP_ATTR = "PIP_ATTR"

    def __str__(self) -> str:
        return str(self.value)
