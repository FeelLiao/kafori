from datetime import date
from tortoise import fields
from pydantic import BaseModel
from typing import Optional

# ------------ 响应模型（可选） ------------
class Home(BaseModel):


    class Config:
        from_attributes=True