from sqlalchemy import (Column, Integer, String, Boolean, Enum, Date, Time, ForeignKey)
from sqlalchemy.orm import relationship
from database import Base, engine
import enum


class DeliveryStatus(enum.Enum):
    SENT = "SENT"
    OPENED = "OPENED"


class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    delivery_status = Column(Enum(DeliveryStatus), default=DeliveryStatus.SENT)
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time, nullable=False)

    # company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    # company = relationship("Company", back_populates="campaigns")

    email_template_id = Column(Integer, ForeignKey("email_template.id"), nullable=False)
    email_template = relationship("EmailTemplate", back_populates="campaigns")


