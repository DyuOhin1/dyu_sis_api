from enum import Enum


class Collection(Enum):
    """MongoDB 集合名稱"""
    STUDENT = "students"
    COURSE = "courses"
    GRADUATION = "graduation"
    
    def __str__(self) -> str:
        """返回集合名稱字符串"""
        return self.value 