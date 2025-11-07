from uuid import UUID

from pydantic import BaseModel, field_validator, field_serializer, ConfigDict
from sqlmodel import Field, Relationship, SQLModel


class CategoryGetResponse(BaseModel):
    id: str
    name: str
    username: str
    archived: bool


class Category(SQLModel, table=True):
    __tablename__ = "category"
    id: UUID = Field(primary_key=True)
    name: str
    username: str
    archived: bool
    spends: list["Spend"] = Relationship(back_populates="category")
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('id', mode='before')
    @classmethod
    def validate_uuid(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value

    @field_serializer('id')
    def serialize_id(self, value):
        return str(value) if value else None
