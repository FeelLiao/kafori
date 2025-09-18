from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter

import aiofiles
from fastapi import Header, HTTPException, Request, status
from backend.api.config import config
import contextlib

test_router = APIRouter()

# 根目录白名单（务必改成你的安全目录）
UPLOAD_ROOT = Path(config.upstream.upload_rawdata_dir).resolve()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

# 可选：设置一个最大体积（字节），超过则拒绝
MAX_BYTES: Optional[int] = None  # 例如 10 * 1024**3  # 10 GiB


def sanitize_filename(name: str) -> str:
    """
    简单的文件名清理，去除路径分隔与可疑字符。
    不要直接信任客户端 filename。
    """
    name = os.path.basename(name).strip().replace("\x00", "")
    # 也可加入白名单校验，如只允许字母数字下划线点号等
    return name


def safe_target_path(filename: str) -> Path:
    filename = sanitize_filename(filename)
    target = (UPLOAD_ROOT / filename).resolve()
    # 防止路径穿越
    # Python 3.9+ 可用 is_relative_to
    if not target.is_relative_to(UPLOAD_ROOT):
        raise HTTPException(
            status_code=400, detail="Invalid filename/path.")
    return target


@test_router.put("/upload", status_code=status.HTTP_201_CREATED)
async def upload_raw(
    request: Request,
    # 元数据可从查询参数传递
    filename: str,
    # 可选：让客户端传 content length 与哈希方便校验
    content_length: Optional[int] = Header(
        default=None, alias="Content-Length"),
    x_sha256: Optional[str] = Header(default=None, alias="X-Content-SHA256"),
):
    """
    原始流上传：客户端以 application/octet-stream 直传请求体。
    例：curl -T bigfile.bin "http://localhost:8000/upload?filename=bigfile.bin" -H 
    "Content-Type: application/octet-stream"
    可选：加上 -H "X-Content-SHA256: <hex_sha256>" 提供校验
    """
    if request.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/octet-stream":
        raise HTTPException(
            status_code=415, detail="Content-Type must be application/octet-stream")

    target = safe_target_path(filename)
    if target.exists():
        raise HTTPException(
            status_code=409, detail="Target file already exists")

    # 先写 .part，成功后原子重命名，避免部分写入暴露
    tmp = target.with_suffix(target.suffix + ".part")
    tmp.parent.mkdir(parents=True, exist_ok=True)

    hasher = hashlib.sha256() if x_sha256 else None
    total = 0

    try:
        async with aiofiles.open(tmp, "wb") as f:
            async for chunk in request.stream():
                if not chunk:
                    continue
                total += len(chunk)
                if MAX_BYTES is not None and total > MAX_BYTES:
                    raise HTTPException(
                        status_code=413, detail="Payload too large")
                if hasher:
                    hasher.update(chunk)
                await f.write(chunk)
    except Exception:
        # 发生异常时尽量清理残留
        with contextlib.suppress(Exception):
            if tmp.exists():
                tmp.unlink()
        raise

    # 校验 Content-Length（如提供）
    if content_length is not None and total != int(content_length):
        with contextlib.suppress(Exception):
            tmp.unlink()
        raise HTTPException(
            status_code=400,
            detail=f"Content-Length mismatch: got={total}, expected={content_length}",
        )

    # 校验哈希（如提供）
    if hasher:
        digest = hasher.hexdigest()
        if digest.lower() != x_sha256.lower():
            with contextlib.suppress(Exception):
                tmp.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"SHA256 mismatch: got={digest}, expected={x_sha256}",
            )

    # 原子移动到最终文件名
    os.replace(tmp, target)

    return {
        "saved_to": str(target),
        "size": total,
        "sha256": hasher.hexdigest() if hasher else None,
    }
