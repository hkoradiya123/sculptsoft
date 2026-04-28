from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime
from app.database import Base


class PerformanceLog(Base):
    __tablename__ = "performance_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_date = Column(DateTime, nullable=False)
    runs_scored = Column(Integer, default=0)
    wickets_taken = Column(Integer, default=0)
    match_type = Column(String(20), default="friendly")  # friendly, league, tournament
    opponent = Column(String(100), nullable=True)
    performance_rating = Column(Float, default=0.0)  # 0-10 scale
    notes = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PerformanceLog user_id={self.user_id}>"
