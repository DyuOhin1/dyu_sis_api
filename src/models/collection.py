from enum import Enum


class Collection(Enum):
    """MongoDB 集合名稱"""
    STUDENT_PROFILE = "student_profile"
    STUDENT_SEMESTER = "student_semester"
    COURSE_ATTENDANCE = "course_attendance"
    COURSE_TIMETABLE = "course_timetable"
    COURSE_WARNING = "course_warning"
    PERFORMANCE_GRADE = "performance_grade"
    ANNUAL_GRADE = "annual_grade"
    MILITARY = "military"
    INJURY = "injury"
    ADVISORS = "advisors"
    ADVISOR_INFO = "advisor_info"
    REWARDS_AND_PENALTIES = "rewards_and_penalties"
    PROOF_OF_ENROLLMENT = "proof_of_enrollment"
    SCHOLARSHIP = "scholarship"
    PRINTER_POINTS = "printer_points"
    DORM = "dorm"
    GRADUATION = "graduation"
    GRADUATION_WORKPLACE = "graduation_workplace"
    GRADUATION_ENGLISH = "graduation_english"
    GRADUATION_CHINESE = "graduation_chinese"
    GRADUATION_COMPUTER = "graduation_computer"

    def __str__(self) -> str:
        """返回集合名稱字符串"""
        return self.value 