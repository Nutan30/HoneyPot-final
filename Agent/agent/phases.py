from enum import Enum

class Phase(Enum):
    HOOK = "hook"
    CLARIFICATION = "clarification"
    PROBING = "probing"
    DELAY = "delay"
    EXIT = "exit"
