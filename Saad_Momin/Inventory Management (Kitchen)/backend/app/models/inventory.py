from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Float)
    unit = Column(String)
    category = Column(String)
    value_per_unit = Column(Float, nullable=True)  # Store price per unit
    estimated_value = Column(Float, nullable=True)  # Store total estimated value
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    expiration_tracking = relationship(
        "ExpirationTracker",
        back_populates="item",
        cascade="all, delete-orphan"
    )