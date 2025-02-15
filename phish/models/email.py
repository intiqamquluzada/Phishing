from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

from database import Base, engine


class EmailTemplate(Base):
    __tablename__ = "email_template"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String(150), nullable=True)
    difficulty = Column(String(150), nullable=False)
    subject = Column(String(150), nullable=True)
    body = Column(String(150), nullable=True)
    file_path = Column(String(150), nullable=False)

    campaigns = relationship("Campaign", back_populates="email_template")
    read_events = relationship("EmailReadEvent", back_populates="template", cascade="all, delete-orphan")


class EmailReadEvent(Base):
    __tablename__ = "email_read_event"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("email_template.id"))
    uuid = Column(String(150), unique=True, index=True)

    template = relationship("EmailTemplate", back_populates="read_events")


