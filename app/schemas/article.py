from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ArticleCreate(BaseModel):
    title: str
    content: str
    image: str | None = None
    category_ids: list[UUID]


class ArticleUpdate(BaseModel):
    title: str
    content: str
    image: str | None = None
    category_ids: list[UUID]


class ArticleRead(BaseModel):
    id: UUID
    title: str
    content: str
    image: str | None
    author_id: UUID
    category_ids: list[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
