from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class TimestampMixin(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column(init=False, repr=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, repr=False, server_default=func.now(), onupdate=func.now()
    )


class Base(DeclarativeBase, MappedAsDataclass): ...
