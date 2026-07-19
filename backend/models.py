from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import date

class Expense(Base):
    __tablename__ = "expenses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    merchant: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column()
    category: Mapped[str] = mapped_column()
    expense_date: Mapped[date | None] = mapped_column(nullable=False)
    
