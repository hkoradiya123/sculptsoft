from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class FinanceTransaction(Base):
    __tablename__ = "finance_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_type = Column(String(20), nullable=False)  # credit, debit
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)  # premium_payment, guest_fund, manual
    description = Column(String(255), nullable=True)
    reference_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FinanceTransaction {self.transaction_type} {self.amount}>"
