from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ------------ 请求模型 ------------
class SampleDTO(BaseModel):
    UniqueID: Optional[str] = None # 唯一主键段1
    UniqueEXID: str = Field(..., description="实验编号")
    Filename: Optional[str] = None
    SampleID: str = Field(..., description="样本 id")
    CollectionTime: date = Field(..., description="采集时间")
    SampleAge: Optional[int] = None
    CollectionPart: str = Field(..., description="采集部位")
    SampleDetail: Optional[str] = None
    DepositDatabase: Optional[str] = None
    Accession: Optional[str] = None
    Origin: Optional[str] = None


    model_config = ConfigDict(from_attributes=True)



class SampleCreate(BaseModel):
    UniqueID: int
    UniqueEXID: int
    SampleID: str
    CollectionTime: date
    CollectionPart: str | None = None
    SampleAge: int | None = None

    model_config = ConfigDict(from_attributes=True)

class SampleUpdate(BaseModel):
    SampleAge: int | None = None
    CollectionPart: str | None = None

    model_config = ConfigDict(from_attributes=True)

