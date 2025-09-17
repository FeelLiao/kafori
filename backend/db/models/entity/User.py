from tortoise import fields
from tortoise.models import Model
from datetime import datetime

class User(Model):
    Id = fields.BigIntField(primary_key=True, source_field="id", description='用户 ID')
    Username = fields.CharField(max_length=20, unique=True, source_field="username", description='用户名')
    Password = fields.CharField(max_length=64, source_field="password", description='用户密码')
    Phone = fields.CharField(max_length=11, unique=True, null=True, source_field="phone", description='用户手机号')
    Email = fields.CharField(max_length=128, unique=True, source_field="email", description='用户邮箱')
    UserAvatar = fields.CharField(max_length=255, null=True, source_field="user_avatar", description='用户头像')
    Introduction = fields.CharField(max_length=255, null=True, source_field="introduction", description='用户简介')
    CreateTime = fields.DatetimeField(source_field="create_time", description='用户创建时间')
    UpdateTime = fields.DatetimeField(source_field="update_time", description='用户修改时间')
    Status = fields.SmallIntField(source_field="status", description='用户状态：0-启用，1-禁用')

    class Meta:
        table = 'user'
        row_format = 'DYNAMIC'

    def __str__(self):
        return f"User(id={self.Id}, username={self.Username})"