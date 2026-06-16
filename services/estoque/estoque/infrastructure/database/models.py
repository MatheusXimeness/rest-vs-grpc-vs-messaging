from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from estoque.infrastructure.database.connection import Base


class StockModel(Base):
    __tablename__ = "stocks"

    product_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(255))
    quantity_available: Mapped[int] = mapped_column()
    quantity_reserved: Mapped[int] = mapped_column(default=0)
