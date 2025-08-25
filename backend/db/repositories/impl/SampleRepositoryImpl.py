from datetime import date
from typing import Optional

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from backend.db.repositories.SampleRepository import SampleRepository
from backend.db.models.dto.SampleDTO import SampleDTO


class SampleRepositoryImpl(SampleRepository):

    async def createOneSample(self, body: SampleDTO) -> bool:
        data = body.dict()
        print(data)
        # 手工移除 generated 列
        result = await self.create(**data)
        return bool(result)
        # return True

    async def deleteOneSample(self, unique_id: int) -> bool:
        result = await self.delete_by_id(unique_id)
        return bool(result)

    async def updateOneSample(self, unique_id: int, body: SampleDTO) -> bool:
        data = body.dict(exclude_unset=True)
        result = await self.update_by_id(unique_id, **data)
        return bool(result)

    async def getOneSample(self, unique_id: int) -> SampleDTO:
        result = await self.get_by_id(unique_id)
        return SampleDTO.from_orm(result)

    async def getSampleBySampleID(self, sample_id: str) -> SampleDTO | None:
        try:
            exp = await self.model.get(SampleID=sample_id)
            return SampleDTO.from_orm(exp)
        except DoesNotExist:
            # 直接返回 None
            return None

    async def getSampleByUniqueExId(self, unique_ex_id: str) -> list[dict]:
        sql = """
            SELECT unique_id as UniqueID,
                   sample_id as SampleID,
                   sample as Sample,
                   sample_age as SampleAge,
                   sample_detail as SampleDetail,
                   deposit_database as DepositDatabase,
                   accession as Accession,
                   origin as Origin,
                   collection_part as CollectionPart,
                   collection_time as CollectionTime
            FROM sample
            WHERE unique_ex_id = %s
            ORDER BY collection_time DESC;
        """
        conn = Tortoise.get_connection("default")
        return await conn.execute_query_dict(sql, [unique_ex_id])

    async def getSampleByPartTime(
            self,
            collection_part: Optional[str] = None,
            start_time: Optional[date] = None,
            end_time: Optional[date] = None,
    ) -> list[dict]:

        conn = Tortoise.get_connection("default")

        # 动态拼接条件
        conditions = []
        params = []

        if collection_part is not None:
            conditions.append("collection_part = %s")
            params.append(collection_part)

        if start_time is not None:
            conditions.append("collection_time >= %s")
            params.append(start_time)

        if end_time is not None:
            conditions.append("collection_time <= %s")
            params.append(end_time)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
            SELECT unique_id      AS UniqueID,
                   sample_id      AS SampleID,
                   sample         AS Sample,
                   sample_age     AS SampleAge,
                   sample_detail  AS SampleDetail,
                   deposit_database AS DepositDatabase,
                   accession      AS Accession,
                   origin         AS Origin,
                   collection_part AS CollectionPart,
                   collection_time AS CollectionTime
            FROM sample
            WHERE {where_clause}
            ORDER BY collection_time DESC;
        """
        return await conn.execute_query_dict(sql, params)

    async def getSampleByAgeTimePart(
            self,
            min_age: Optional[int] = None,
            max_age: Optional[int] = None,
            start_time: Optional[date] = None,
            end_time: Optional[date] = None,
            collection_part: Optional[str] = None,
    ) -> list[dict]:

        conn = Tortoise.get_connection("default")

        conditions: list[str] = []
        params: list = []

        # 年龄区间
        if min_age is not None:
            conditions.append("sample_age >= %s")
            params.append(min_age)
        if max_age is not None:
            conditions.append("sample_age <= %s")
            params.append(max_age)

        # 时间区间
        if start_time is not None:
            conditions.append("collection_time >= %s")
            params.append(start_time)
        if end_time is not None:
            conditions.append("collection_time <= %s")
            params.append(end_time)

        # 部位
        if collection_part is not None:
            conditions.append("collection_part = %s")
            params.append(collection_part)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
            SELECT unique_id      AS UniqueID,
                   sample_id      AS SampleID,
                   sample         AS Sample,
                   sample_age     AS SampleAge,
                   sample_detail  AS SampleDetail,
                   deposit_database AS DepositDatabase,
                   accession      AS Accession,
                   origin         AS Origin,
                   collection_part AS CollectionPart,
                   collection_time AS CollectionTime
            FROM sample
            WHERE {where_clause}
            ORDER BY collection_time DESC;
        """
        return await conn.execute_query_dict(sql, params)

    async def get_sample_by_unique_ex_id_and_part_time(
            self,
            unique_ex_id: tuple[str],
            collection_part: Optional[tuple[str]] = None,
            start_time: Optional[date] = None,
            end_time: Optional[date] = None,
    ) -> list[dict]:
        """
        Get sample data for a specific unique experiment ID, optionally filtered by collection parts and time range.

        Args:
            unique_ex_id (Tuple[str]): Tuple of unique experiment identifiers.
            collection_part (Optional[Tuple[str]]): Tuple of collection parts to filter by. Defaults to None.
            start_time (Optional[date]): Start time of the collection time range. Defaults to None.
            end_time (Optional[date]): End time of the collection time range. Defaults to None.

        Returns:
            List[Dict]: List of dictionaries containing sample data.
        """
        conn = Tortoise.get_connection("default")

        # 动态拼接条件
        conditions = ["unique_ex_id IN ({})".format(", ".join(["%s"] * len(unique_ex_id)))]
        params = list(unique_ex_id)

        if collection_part is not None:
            conditions.append("collection_part IN ({})".format(", ".join(["%s"] * len(collection_part))))
            params.extend(collection_part)

        if start_time is not None:
            conditions.append("collection_time >= %s")
            params.append(start_time)

        if end_time is not None:
            conditions.append("collection_time <= %s")
            params.append(end_time)

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT unique_id      AS UniqueID,
                   sample_id      AS SampleID,
                   sample         AS Sample,
                   sample_age     AS SampleAge,
                   sample_detail  AS SampleDetail,
                   deposit_database AS DepositDatabase,
                   accession      AS Accession,
                   origin         AS Origin,
                   collection_part AS CollectionPart,
                   collection_time AS CollectionTime
            FROM sample
            WHERE {where_clause}
            ORDER BY collection_time DESC;
        """
        return await conn.execute_query_dict(sql, params)
