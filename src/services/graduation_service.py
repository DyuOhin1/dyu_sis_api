from typing import Optional
from ..models.graduation import GraduationRequirement
from ..utils.cache import get_cache, set_cache
from ..config import settings

class GraduationService:
    @staticmethod
    async def get_graduation_requirements(student_id: str, refresh: bool = False) -> Optional[GraduationRequirement]:
        # 嘗試從快取獲取資料
        cache_data = await get_cache("graduation_requirements", student_id, refresh)
        if cache_data and not refresh:
            return GraduationRequirement(**cache_data)

        # TODO: 從 SIS 系統獲取畢業門檻資訊
        # 這裡先模擬資料
        requirements = GraduationRequirement(
            student_id=student_id,
            english_qualified=False,
            chinese_qualified=True,
            computer_qualified=False,
            workplace_exp_qualified=True,
            total_credits=120,
            required_credits=90,
            elective_credits=30,
            is_qualified=False
        )

        # 更新快取
        await set_cache(
            "graduation_requirements",
            student_id,
            requirements.model_dump(),
            settings.CACHE_DURATION
        )

        return requirements

    @staticmethod
    async def get_graduation_pdf(student_id: str) -> Optional[bytes]:
        # TODO: 實作獲取畢業審查表 PDF 的邏輯
        return None 