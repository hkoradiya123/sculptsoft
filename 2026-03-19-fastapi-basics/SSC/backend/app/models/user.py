from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # Profile
    jersey_number = Column(Integer, nullable=True)
    role = Column(String(50), default="player")  # player, admin
    bio = Column(String(500), nullable=True)
    
    # Stats
    runs = Column(Integer, default=0)
    matches = Column(Integer, default=0)
    wickets = Column(Integer, default=0)
    centuries = Column(Integer, default=0)
    half_centuries = Column(Integer, default=0)
    average_runs = Column(Float, default=0.0)
    highest_score = Column(Integer, default=0)
    
    # Premium Subscription
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime, nullable=True)
    premium_start_date = Column(DateTime, nullable=True)
    
    # Account Management
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"
