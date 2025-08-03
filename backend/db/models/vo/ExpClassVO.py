from datetime import date
from pydantic import BaseModel

# ------------ 响应模型（可选） ------------
class SampleOut(BaseModel):
    unique_id: int
    sample_id: str
    collection_time: date
    collection_part: str
    sample_age: int | None = None

    class Config:
        orm_mode = True   # 让 Tortoise 对象可以直接返回