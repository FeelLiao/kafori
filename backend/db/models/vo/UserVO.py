from datetime import date
from tortoise import fields
from pydantic import BaseModel
from typing import Optional

# ------------ 响应模型（可选） ------------
class UserVO(BaseModel):
    Id: int = fields.BigIntField(primary_key=True, source_field="id", description='用户 ID')
    Username: str = fields.CharField(max_length=20, unique=True, source_field="username", description='用户名')
    Phone: Optional[str] = fields.CharField(max_length=11, unique=True, null=True, source_field="phone", description='用户手机号')
    Email: Optional[str] = fields.CharField(max_length=128, unique=True, source_field="email", description='用户邮箱')
    UserAvatar: Optional[str] = fields.CharField(max_length=255, null=True, source_field="user_avatar", description='用户头像')
    Introduction: Optional[str] = fields.CharField(max_length=255, null=True, source_field="introduction", description='用户简介')

    class Config:
        from_attributes=True