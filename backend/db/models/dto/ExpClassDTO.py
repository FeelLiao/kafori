from pydantic import BaseModel,ConfigDict

# ------------ 请求模型 ------------
class ExpClassDTO(BaseModel):
    ExpClass: str | None = None
    ExperimentCategory: str | None = None

    model_config = ConfigDict(from_attributes=True)  # 不再报警


