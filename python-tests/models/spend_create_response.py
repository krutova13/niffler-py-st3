from pydantic import BaseModel


class Category(BaseModel):
    id: str
    name: str
    username: str
    archived: bool


class SpendResponse(BaseModel):
    id: str
    spendDate: str
    category: Category
    currency: str
    amount: float
    description: str
    username: str
