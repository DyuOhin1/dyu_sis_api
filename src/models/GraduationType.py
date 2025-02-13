from enum import Enum


class GraduationType(str, Enum):
    CHINESE = "chinese"
    ENGLISH = "english"
    COMPUTER = "computer"
    WORKPLACE_EXP = "workplace_exp"
    OVERVIEW = "overview"