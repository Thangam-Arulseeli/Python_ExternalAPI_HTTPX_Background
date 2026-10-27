from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ExternalUser(BaseModel):
    model_config = ConfigDict(
        extra="ignore",     # unexpected fields are ignored
        strict=True,    # strict=True requests strict type validation, reducing implicit conversions
    )

    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    username: str = Field(min_length=1)
    email: EmailStr

