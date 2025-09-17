from tortoise import fields
from pydantic import BaseModel
from typing import Optional

# ------------ 响应模型（可选） ------------
class UserDTO(BaseModel):
    username: str = fields.CharField(max_length=20, unique=True, source_field="username", description='用户名')
    password: str = fields.CharField(max_length=64, source_field="password", description='用户密码')

    class Config:
        from_attributes=True