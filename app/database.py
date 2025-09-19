from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
import enum
from datetime import datetime

from .config import settings

# Define enums to match the choices in the original schema
class TradeType(str, enum.Enum):
    CALL = "CALL"
    PUT = "PUT"

class TradeStatus(str, enum.Enum):
    ACTIVE = "Active"
    CLOSED = "Closed"

# SQLAlchemy setup
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ORM Model for the Trades table
class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, comment="The full OCC option symbol")
    trade_type = Column(Enum(TradeType), comment="CALL or PUT")
    underlying = Column(String, index=True, comment="The stock ticker")
    strike = Column(Float, comment="The option's strike price")
    entry_price = Column(Float, comment="The price at which the trade was initiated")
    current_price = Column(Float, comment="The last known price, updated periodically")
    peak_price_today = Column(Float, comment="The highest price reached during the day")
    exit_price = Column(Float, nullable=True, comment="The final price when the trade is closed")
    expiration_date = Column(DateTime, comment="The expiration date in ISO format")
    status = Column(Enum(TradeStatus), default=TradeStatus.ACTIVE)
    close_reason = Column(String, nullable=True, comment="Why the trade was closed")
    entry_image = Column(String, nullable=True, comment="The Base64 string of the initial trade alert image")
    peak_image = Column(String, nullable=True, comment="The Base64 string of the latest peak price alert image")
    last_goal_achieved = Column(Integer, default=0, comment="The last profit goal reached (0-5)")
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

def init_db():
    """
    Initializes the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency function to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
