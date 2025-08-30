### 简介

**FastAPI** is a modern, high-performance async web framework for building APIs using Python. It is designed to be fast, easy to use, and production-ready. Built on **Starlette** for web handling and **Pydantic** for data validation, FastAPI leverages Python's type hints to provide robust features like automatic validation, serialization, and interactive API documentation.

FastAPI 是一个现代、高性能的异步 Web 框架，用于使用 Python 构建 API。它被设计得快速、易于使用且可用于生产环境。FastAPI 基于 Starlette 构建，用于 Web 处理，Pydantic 用于数据验证，它利用 Python 的类型提示来提供强大的功能，如自动验证、序列化和交互式 API 文档。

### 快速启动fastapi

准备好python环境，推荐使用3.10+
pip创建
```bash
# 创建项目目录
mkdir fastapi-demo
cd fastapi-demo

python -m venv .venv

# 激活虚拟环境 (Windows CMD)
.venv/Scripts/activate
# linux环境
source .venv/bin/activate

```

安装fastapi依赖

```bash
pip install fastapi "uvicorn[standard]" pydantic
```
- `fastapi`: 核心框架。
- `uvicorn[standard]`: ASGI 服务器，`[standard]` 会带来一些额外的优化库。
- `pydantic`: FastAPI 内部使用它进行数据验证和序列化，虽然 FastAPI 会自动安装，但显式安装有助于理解。

编写一个简单的示例

```python
# main.py
from fastapi import FastAPI

# 1. 创建 FastAPI 实例
app = FastAPI()

# 2. 定义一个 API 端点 (路径操作装饰器)
@app.get("/")  # 当有 GET 请求访问根路径 "/" 时，执行下面的函数
async def read_root():
    # 3. 返回 JSON 响应
    return {"message": "Hello, FastAPI World!"}

@app.get("/hello")
async def say_hello():
    return {"greeting": "大家好，我是旺仔小乔，你们好吗！"}
```


### fastapi生命周期

fastapi实例化之后是全局的，只要项目运行，这个实例就是一直存在，并且只有一个实例，并且fastapi也与中间件、数据库和自定义服务都做了很好的兼容，我们可以将其他的服务和fastapi绑定在一起，可以做一个集中管理，下面给出几个示例：

**mysql/oracle/postgresql**等关系型数据库:
- 实例化FastAPI
- tortoise配置好连接参数
- tortoise注册到FastAPI

```python
# main.py
#这个tortoise是关系型数据库的操作接口库，后续会讲
from tortoise.contrib.fastapi import register_tortoise
#实例化fastapi
app = FastAPI()

#将数据库api, tortoise-orm注册到fastapi
register_tortoise(  
    app,  
    config=TORTOISE_ORM,  #配置参数
    generate_schemas=False,  # 生产环境用迁移  
    add_exception_handlers=True,   #开启异常处理
)
```

```python
#关系型数据库模版配置参数
TORTOISE_ORM = {  
    "connections": {  
        "default": {  
            "engine": "tortoise.backends.mysql",  #引擎(这里是mysql)
            "credentials": {  
                "host":     settings.mysql.host,  #mysql主机，改成自己的主机ip
                "port":     settings.mysql.port,  #端口
                "user":     settings.mysql.user,  #用户名
                "password": settings.mysql.password,  #密码
                "database": settings.mysql.database,  #连接数据库
                "charset":  settings.mysql.charset,  #字符集
                "minsize":  settings.mysql.pool_size,  #最小连接数
                "maxsize":  settings.mysql.max_pool_size,  #最大连接数
                "echo":     settings.mysql.echo,  #是否打印sql(bool)
                "pool_recycle": settings.mysql.pool_recycle,  # 连接回收时间(秒)
            },  
        }  
    },  
    "apps": {  
        "models": {  #这里就是你的数据库映射模型-表
            "models": ["backend.db.models.entity"],  #模型定义的目录
            "default_connection": "default",  #默认连接名，不需要修改
        }  
    },  
}
```

**redis等非关系型数据库**
- 实例化FastAPI
- lifespan管理生命周期
- 将redis注册到lifespan

```python
#定义一个异步文件管理器，用户FastAPI的生命周期管理
@asynccontextmanager  
async def lifespan(app: FastAPI):  
	#将redis连接池实例注册到FastAPI中，使用app.state操作
    app.state.redis = build_redis_pool()  
    logger.info("Redis connection pool initialized")  
    yield  #下面定义FastAPI销毁时对应的操作
    #销毁redis实例
    await app.state.redis.close()  
    logger.info("Redis connection pool closed")  
  
  
app = FastAPI(lifespan=lifespan,  #直接注册到这里管理
              title="Kafori API",  
              description="API for Kafori project",  
              version="1.0.0",  
              license_info={  
                  "name": "MIT",  
                  "url": "https://opensource.org/licenses/MIT"  
              }  
              )
```

**异常处理类**
我们在实际开发项目中很需要异常处理来帮我们自动捕获异常，这样可以很大程度减少try...catch操作，这样我们可以定义一个异常处理类注册到FastAPI中来查找FastAPI中的异常，当然也包括其他注册到FastAPI中的实例

```python
#main.py
from handler import ExceptionHandler
# 注册异常处理器（一行即可）  
ExceptionHandler.register(app)
```

```python
#handler.py
class ExceptionHandler:  
    """  
    统一异常处理器  
    1. ValidationError    -> 422    2. IntegrityError     -> 400    3. 其他 Exception     -> 500    """  
    @staticmethod  
    def register(app):  
	    #这里需要将我们遇到的异常进行对应的函数处理，可以写一个模版
        """一次性注册到 FastAPI"""
        app.add_exception_handler(  
            ValidationError,  ExceptionHandler.validation_error)  
        app.add_exception_handler(  
            IntegrityError,   ExceptionHandler.integrity_error)  
        app.add_exception_handler(  
            Exception,        ExceptionHandler.generic_error)  
  
    # ---------- 具体处理函数 ----------    @staticmethod  
    async def validation_error(request: Request, exc: Exception) -> JSONResponse:  
        return JSONResult.error("参数校验失败", status_code=422)  
  
    @staticmethod  
    async def integrity_error(request: Request, exc: Exception) -> JSONResponse:  
        return JSONResult.error("数据已存在或约束冲突", status_code=400)  
  
    @staticmethod  
    async def generic_error(request: Request, exc: Exception) -> JSONResponse:  
        # 可在此处记录日志  
        return JSONResult.error("服务器内部错误", status_code=500)
```
