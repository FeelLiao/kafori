from typing import TypeVar, Generic, Type, Optional, List

from tortoise.expressions import Q
from tortoise.models import Model

ModelT = TypeVar("ModelT", bound=Model)

class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    async def create(self, **kwargs) -> ModelT:
        return await self.model.create(**kwargs)

    async def get_by_id(self, *pk) -> Optional[ModelT]:
        q_objs = [Q(pk=val) for val in pk]
        return await self.model.get_or_none(*q_objs)

    async def update_by_id(self, *pk, **kwargs) -> int:
        # 把每个位置参数转成 Q
        q_objs = [Q(pk=val) for val in pk]
        return await self.model.filter(*q_objs).update(**kwargs)

    async def delete_by_id(self, *pk) -> int:
        # 把每个位置参数转成 Q
        q_objs = [Q(pk=val) for val in pk]
        return await self.model.filter(*q_objs).delete()

    async def list(self, limit: int = 100, offset: int = 0) -> List[ModelT]:
        return await self.model.all().limit(limit).offset(offset)

    async def count(self) -> int:
        return await self.model.all().count()