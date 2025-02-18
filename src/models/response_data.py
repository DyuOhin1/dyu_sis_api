from pydantic import BaseModel


class ResponseData(BaseModel):
    data: dict = None