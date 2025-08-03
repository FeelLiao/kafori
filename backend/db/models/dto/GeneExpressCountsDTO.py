from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class GeneExpressCountsDTO(BaseModel):
    UniqueID: Optional[str] = None # 唯一主键段1
    SampleID: str = Field(..., description="样本 id")
    GeneID: str = Field(..., description="基因id")
    Counts:float = Field(..., description="counts数据")

    model_config = ConfigDict(from_attributes=True)