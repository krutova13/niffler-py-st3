from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictFloat
from sqlmodel import Field, SQLModel, Relationship

from models.category import Category


class Spend(SQLModel, table=True):
    __tablename__ = "spend"
    id: str = Field(primary_key=True)
    spend_date: datetime
    currency: str
    amount: float
    description: str
    username: str
    category_id: str = Field(foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="spends")


class SpendRequest(BaseModel):
    amount: str
    currency: str
    spendDate: str
    category: dict[str, str]
    description: str = ""


class SpendResponse(BaseModel):
    id: str
    spendDate: str
    category: Category
    currency: str
    amount: StrictFloat
    description: str
    username: str


class SpendModelAdd(BaseModel):
    amount: float
    currency: str
    spendDate: str
    description: str
    category: dict[str, str]
    username: str


class ErrorResponseModel(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
