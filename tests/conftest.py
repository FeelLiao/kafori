
import pytest_asyncio
from tortoise import Tortoise


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db():
    await Tortoise.init(
        db_url="mysql://root:mysql_zxtASb@127.0.0.1:3306/kafori",
        modules={"models": ["backend.db.models.entity"]}  # 必须是模块路径
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()