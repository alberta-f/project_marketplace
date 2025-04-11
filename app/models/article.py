import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# many-to-many table
article_category = Table(
    "article_category",
    Base.metadata,
    Column("article_id", UUID, ForeignKey("articles.id")),
    Column("category_id", UUID, ForeignKey("categories.id")),
)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str]
    image: Mapped[str | None]
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)
    deleted: Mapped[bool] = mapped_column(default=False)

    categories = relationship("Category",
                              secondary=article_category,
                              backref="articles",
                              lazy="selectin")

    @property
    def category_ids(self) -> list[UUID]:
        return [category.id for category in self.categories]
