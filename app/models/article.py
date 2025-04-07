import uuid

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Article(Base):
    __tablename__ = 'articles'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
