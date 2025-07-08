from pydantic import BaseModel, StrictFloat


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
    amount: StrictFloat
    description: str
    username: str
