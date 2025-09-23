from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from backend.db.interface import DataBase
from backend.db.result.Result import Result
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
    username: str
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        user_rec = await db.user.model.filter(Username=username).first()
        if not user_rec:
            raise credentials_exception
        # 构造当前用户对象（与其他路由类型兼容）
        disabled_flag = False
        for attr in ("Disabled", "disabled"):
            if hasattr(user_rec, attr):
                disabled_flag = bool(getattr(user_rec, attr))
                break
        return User(username=username, disabled=disabled_flag)
    except InvalidTokenError:
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[UserVO, Depends(get_current_user)],
):
    return current_user


@validation_router.post("/user/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await db.user.model.filter(Username=form_data.username).first()
    if not user or not verify_password(form_data.password, user.Password):
        # 符合 OAuth2 密码流规范的错误返回
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.Username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@validation_router.get("/user/getUserInfo")
async def get_current_user_info(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return Result.error(message='Token could not validate credentials')
        user = await db.user.model.filter(Username=username).first()
        if not user:
            return Result.error(message='user not found')
        user_vo = UserVO.model_validate(user)  # 适合pydantic v2
        return Result.success(message="用户信息获取成功", data=user_vo.model_dump(by_alias=True))
    except InvalidTokenError:
        return Result.error(message='Token could not validate credentials')

