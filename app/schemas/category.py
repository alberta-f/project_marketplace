from uuid import UUID

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str


class CategoryRead(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_node = True
