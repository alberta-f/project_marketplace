from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import Form
from pydantic import BaseModel


class ArticleCreate(BaseModel):
    title: str
    content: str
    category_ids: List[UUID]

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        content: str = Form(...),
        category_ids: List[UUID] = Form(...),
    ):
        return cls(
            title=title,
            content=content,
            category_ids=category_ids
        )



class ArticleUpdate(BaseModel):
    title: str
    content: str
    category_ids: List[UUID]

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        content: str = Form(...),
        category_ids: List[UUID] = Form(...),
    ):
        return cls(
            title=title,
            content=content,
            category_ids=category_ids
        )


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
