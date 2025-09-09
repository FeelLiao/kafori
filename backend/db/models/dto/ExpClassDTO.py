from pydantic import BaseModel,ConfigDict
from typing import Optional
# ------------ 请求模型 ------------
class ExpClassDTO(BaseModel):
    ExpClass: str
    ExperimentCategory: str
    Experiment: Optional[str] = None
    SampleCounts: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


