import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.category import EmployeeCategory


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String, nullable=True, default="")
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False, default="")
    role_category_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("employee_categories.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_category: Mapped[Optional["EmployeeCategory"]] = relationship(
        "EmployeeCategory", lazy="joined"
    )

    @property
    def role(self) -> str:
        if self.role_category and self.role_category.role:
            return self.role_category.role
        return "operator"
