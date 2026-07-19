from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column()
    category: Mapped[str] = mapped_column()
