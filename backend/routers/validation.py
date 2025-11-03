from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, Field
from backend.db.interface import DataBase
from backend.db.result.Result import Result

from backend.db.models.dto.UserDTO import UserDTO
from backend.db.models.vo.UserVO import UserVO
from backend.api.config import config

validation_router = APIRouter()

SECRET_KEY = config.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

db = DataBase()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str = Field(alias="Username")
    disabled: bool | None = Field(default=None, alias="Disabled")

    model_config = ConfigDict(populate_by_name=True)


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 使用绝对路径，便于 swagger/oauth2 正常解析
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserVO:
    """
    FastAPI dependency: validate Bearer JWT and return UserVO.
    Raises HTTPException(401) on any validation failure.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise credentials_exception

    username = payload.get("sub")
    if not username:
        raise credentials_exception

    # 从真实数据库读取用户
    user_row = await db.user.model.filter(Username=username).first()
    if not user_row:
        raise credentials_exception

    # 把 ORM/记录转换为 UserVO（pydantic v2）
    try:
        user_vo = UserVO.model_validate(user_row)
    except Exception:
        # 若转换失败则拒绝访问
        raise credentials_exception

    return user_vo


async def get_current_active_user(
    current_user: Annotated[UserVO, Depends(get_current_user)],
) -> User:
    # 可在此处检查 current_user.disabled 等字段
    UserInfo = current_user.model_dump(by_alias=True)
    return User.model_validate(UserInfo)


@validation_router.post("/user/login")
async def login_for_access_token(
    userDTO: UserDTO
) -> Result:
    """
    登录接口，返回标准结构 {"access_token": "...", "token_type": "bearer"}。
    客户端在 Authorization 头使用: Authorization: Bearer <token>
    """
    user = await db.user.model.filter(Username=userDTO.username).first()
    if not user:
        return Result.error(message="User not found")
    if not verify_password(userDTO.password, user.Password):
        return Result.error(message="Incorrect password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = 'Bearer ' + create_access_token(
        data={"sub": user.Username}, expires_delta=access_token_expires
    )
    return Result.success(access_token)


@validation_router.get("/user/getUserInfo")
async def get_user_info(current_user: Annotated[UserVO, Depends(get_current_user)]):
    """
    返回当前用户信息（依赖 get_current_user 已验证 token 并返回 UserVO）
    """
    user_vo = current_user
    return Result.success(message="用户信息获取成功", data=user_vo.model_dump(by_alias=True))
