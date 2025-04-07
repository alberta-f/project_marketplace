import uuid

from core.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[String] = mapped_column(nullable=False, unique=True)
