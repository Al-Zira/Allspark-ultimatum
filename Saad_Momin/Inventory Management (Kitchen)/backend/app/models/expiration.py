from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime

class ExpirationStatus(str, enum.Enum):
    GOOD = "good"
    WARNING = "warning"
    EXPIRED = "expired"

class ExpirationTracker(Base):
    __tablename__ = "expiration_tracking"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('inventory_items.id', ondelete='CASCADE'))
    expiration_date = Column(DateTime, nullable=False)
    status = Column(String, default=ExpirationStatus.GOOD)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    item = relationship("InventoryItem", back_populates="expiration_tracking") 