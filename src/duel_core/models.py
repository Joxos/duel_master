from pydantic import BaseModel, ConfigDict


class MutableModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)
