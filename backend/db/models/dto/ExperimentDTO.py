from pydantic import BaseModel, ConfigDict


class ExperimentDTO(BaseModel):
    UniqueEXID: str | None = None
    ExpClass: str | None = None
    Experiment: str | None = None

    model_config = ConfigDict(from_attributes=True)  # 不再报警