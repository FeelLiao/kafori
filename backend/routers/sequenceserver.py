# proxy_sequenceserver.py  (v3.1: 非流式 + 修复多重 Location)
from fastapi import APIRouter, Request, Response
from starlette.responses import RedirectResponse
import httpx
from urllib.parse import urljoin, urlsplit, urlunsplit
import re
from backend.api.config import config
from typing import Dict

router = APIRouter()

UPSTREAM_BASE = config.sequenceserver_url

# 我们在后端内部固定的二级前缀（不包含外层网关前缀，如 /prod-api）
API_PREFIX = "/proxy/sequenceserver/"

# hop-by-hop 头：代理不应透传
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "transfer-encoding", "upgrade",
}
HTML_TYPE_RE = re.compile(r"text/html(?:;|$)", re.I)
REDIRECT_STATUSES = {301, 302, 303, 307, 308}


# ----------------- 工具函数 -----------------
def _visible_prefix(request: Request) -> str:
    """
    计算“客户端可见”的完整前缀：
    - 若反代设置了 X-Forwarded-Prefix=/prod-api，则返回 /prod-api/proxy/sequenceserver/
    - 否则返回 /proxy/sequenceserver/
    - 同时兼容 Uvicorn/FastAPI 的 root_path
    """
    xfp = (request.headers.get("x-forwarded-prefix") or "").rstrip("/")
    root_path = request.scope.get("root_path", "").rstrip("/")
    base = xfp or root_path or ""
    visible = f"{base}{API_PREFIX}"
    if not visible.startswith("/"):
        visible = "/" + visible
    if not visible.endswith("/"):
        visible = visible + "/"
    return visible


def _rewrite_location_with_visible_prefix(location: str, request: Request) -> str:
    if not location:
        return location
    parts = urlsplit(location)
    new_path = parts.path.lstrip("/")
    return urlunsplit(("", "", _visible_prefix(request) + new_path, parts.query, parts.fragment))


def _append_frame_ancestors(csp_value: str, addition: str) -> str:
    """在现有 CSP 上追加 frame-ancestors（若已存在则不追加）。"""
    if csp_value and "frame-ancestors" in csp_value:
        return csp_value
    addition = addition.strip().rstrip(";")
    if not csp_value:
        return addition + ";"
    return csp_value.rstrip(";") + "; " + addition + ";"


def _needs_base_injection(headers: httpx.Headers) -> bool:
    ct = headers.get("content-type", "")
    return bool(HTML_TYPE_RE.search(ct))


def _inject_base(html_bytes: bytes, base_href: str) -> bytes:
    """在 <head> 后注入 <base href=...>；若已有 <base> 则原样返回。"""
    html = html_bytes.decode("utf-8", errors="ignore")
    if re.search(r"<base\s+href=", html, flags=re.I):
        return html_bytes
    new_html = re.sub(
        r"(?i)<head([^>]*)>",
        lambda m: f"<head{m.group(1)}><base href=\"{base_href}\">",
        html,
        count=1,
    )
    return new_html.encode("utf-8")


def _copy_clean_headers(src: httpx.Headers) -> Dict[str, str]:
    """复制响应头，移除 hop-by-hop、X-Frame-Options、(任意大小写)location。"""
    out: Dict[str, str] = {}
    for k, v in src.items():
        kl = k.lower()
        if kl in HOP_BY_HOP:
            continue
        if kl in ("x-frame-options", "location"):
            continue
        out[k] = v
    return out


# ----------------- 核心代理 -----------------
async def _proxy(request: Request, path: str) -> Response:
    # 上游 URL
    upstream_url = urljoin(UPSTREAM_BASE + "/", path)
    if request.url.query:
        upstream_url += f"?{request.url.query}"

    # 请求头：过滤 hop-by-hop，并设置反代识别头；强制上游不压缩（避免解码问题）
    req_headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in HOP_BY_HOP and k.lower() != "host"}
    req_headers["Host"] = urlsplit(UPSTREAM_BASE).netloc
    req_headers["X-Forwarded-Proto"] = request.url.scheme
    req_headers["X-Forwarded-Host"] = request.headers.get("host", "")
    req_headers["X-Forwarded-Prefix"] = (request.headers.get("x-forwarded-prefix") or
                                         request.scope.get("root_path", "") or "")
    req_headers["Accept-Encoding"] = "identity"  # 统一让上游返回未压缩内容

    body = await request.body()

    # 禁用连接复用更稳（避免个别上游断流边界问题）
    limits = httpx.Limits(max_keepalive_connections=0, max_connections=100)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, read=300.0),
        follow_redirects=False,
        limits=limits,
        http2=False,
    ) as client:
        req = client.build_request(
            request.method, upstream_url, headers=req_headers, content=body)
        resp = await client.send(req, stream=False)  # 非流式，一次性读完

        content = resp.content

        # 复制并清洗响应头（此处不处理 Location，最后统一设置一次）
        out_headers = _copy_clean_headers(resp.headers)

        # 允许同源嵌入（不覆盖已有 CSP）
        out_headers["Content-Security-Policy"] = _append_frame_ancestors(
            resp.headers.get("content-security-policy", ""),
            "frame-ancestors 'self'",
        )

        # 统一处理重定向 Location：只发一个大写 Location，且改写为可见前缀
        if resp.status_code in REDIRECT_STATUSES:
            upstream_loc = resp.headers.get(
                "Location") or resp.headers.get("location")
            if upstream_loc:
                out_headers["Location"] = _rewrite_location_with_visible_prefix(
                    upstream_loc, request)

        # 如果是 HTML 文档：注入 <base>（指向“可见前缀”）
        if _needs_base_injection(resp.headers) and resp.status_code == 200 and request.method == "GET":
            try:
                content = _inject_base(content, _visible_prefix(request))
            except Exception:
                # 注入失败则退回原始内容
                pass

        # 统一移除编码与长度（避免编码/长度不匹配；由下游决定是否压缩）
        out_headers.pop("Content-Encoding", None)
        out_headers.pop("content-encoding", None)
        out_headers.pop("Content-Length",   None)
        out_headers.pop("content-length",   None)

        return Response(
            content=content,
            status_code=resp.status_code,
            headers=out_headers,
            media_type=resp.headers.get("content-type"),
        )


# ----------------- 路由 -----------------
@router.get("/proxy/sequenceserver")
async def _add_slash(request: Request):
    """自动补尾斜杠，避免相对资源路径错位。"""
    return RedirectResponse(url=_visible_prefix(request), status_code=302)


@router.api_route("/proxy/sequenceserver/", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
@router.api_route("/proxy/sequenceserver/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE",
                                                                "OPTIONS", "HEAD"])
async def sequenceserver_proxy(request: Request, path: str = ""):
    return await _proxy(request, path)
