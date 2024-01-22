from __future__ import annotations

import datetime

from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class Notes(Base):
    __tablename__ = "notes"

    note_id: Mapped[int] = mapped_column(
        "note_id",
        autoincrement=True,
        primary_key=True,
    )
    title: Mapped[str] = mapped_column("title", nullable=False)
    content: Mapped[str] = mapped_column("content", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        "created_at",
        default=datetime.datetime.utcnow(),
        nullable=True,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        "updated_at",
        default=datetime.datetime.utcnow(),
        nullable=True,
    )
    deleted_at: Mapped[datetime.datetime] = mapped_column(
        "deleted_at",
        nullable=True,
    )
    created_by: Mapped[int] = mapped_column(
        "created_by",
        ForeignKey("users.user_id"),
        nullable=True,
    )
    updated_by: Mapped[int] = mapped_column(
        "updated_by",
        ForeignKey("users.user_id"),
        nullable=True,
    )
    deleted_by: Mapped[int] = mapped_column(
        "deleted_by",
        ForeignKey("users.user_id"),
        nullable=True,
    )


class NotesSchema(BaseModel):
    note_id: int
    title: str
    content: str
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None
    deleted_at: datetime.datetime | None
    created_by: int | None
    updated_by: int | None
    deleted_by: int | None

    class Config:
        from_attributes = True