from tortoise.exceptions import DoesNotExist
from tortoise import Tortoise
import datetime
import uuid
import random

from backend.db.models.entity.ExpClass import ExpClass
from backend.db.models.dto.ExpClassDTO import ExpClassDTO
from backend.db.repositories.ExpClassRepository import ExpClassRepository

# 适合分布式


def generate_unique_id() -> str:
    """生成形如 LRX<YYYYMMDD><8位UUID> 的唯一 ID"""
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    uuid_hex = uuid.uuid4().hex[:8]  # 8位十六进制
    return f"LRX{date_str}{uuid_hex}"


# 适合高并发
def generate_unique_id_2() -> str:
    """生成形如 LRX<YYYYMMDD><3位十六进制随机数><6位十六进制微秒> 的唯一 ID"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    rand_hex = format(random.randint(0, 0xFFF), 'x').zfill(3)  # 3位十六进制随机数
    microsecond_hex = format(now.microsecond, 'x').zfill(6)  # 6位十六进制微秒
    return f"LRX{date_str}{rand_hex}{microsecond_hex}"


class ExpClassRepositoryImpl(ExpClassRepository):

    async def createOneExpClass(self, body: ExpClassDTO) -> bool:
        result = await self.create(**body.__dict__)
        return bool(result)

    async def deleteOneExpClass(self, exp_class: int) -> bool:
        result = await self.delete_by_id(exp_class)
        return bool(result)

    async def updateOneExpClass(self, exp_class: int, body: ExpClassDTO) -> bool:
        data = body.dict(exclude_unset=True)
        result = await self.update_by_id(exp_class, **data)
        return bool(result)

    async def getOneExpClass(self, exp_class: str) -> ExpClass:
        result = await self.get_by_id(exp_class)
        return result

    async def getOneByCategory(self, category: str) -> ExpClassDTO | None:
        try:
            exp = await self.model.get(ExperimentCategory=category)

            # return ExpClassDTO.from_orm(exp)
            return ExpClassDTO.from_orm(exp)
        except DoesNotExist:
            # 如果要自动创建，就创建后再返回；否则直接返回 None
            new_exp = await self.model.create(
                ExpClass=generate_unique_id(),
                ExperimentCategory=category
            )
            return ExpClassDTO.from_orm(new_exp)

    async def getExpClss(self, start_page: int | None = None, size: int | None = None) -> list[dict]:
        conn = Tortoise.get_connection("default")
        if start_page is None or size is None:
            sql_all = """
                SELECT exp_class as ExpClass, experiment_category as ExperimentCategory
                FROM exp_class
                FORCE INDEX (PRIMARY);
            """
            return await conn.execute_query_dict(sql_all)
        if size <= 0 or start_page < 0:
            return []

        sql_page = """
                SELECT exp_class as ExpClass, experiment_category as ExperimentCategory
                FROM exp_class
                FORCE INDEX (PRIMARY)
                LIMIT %s, %s;
            """
        return await conn.execute_query_dict(sql_page, [start_page, size])
