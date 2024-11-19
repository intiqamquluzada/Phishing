from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

from phish.database import Base, engine


class EmailTemplate(Base):
    __tablename__ = "email_template"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    difficulty = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(String, nullable=True)
    file_path = Column(String, nullable=False)

    campaigns = relationship("Campaign", back_populates="email_template")
    read_events = relationship("EmailReadEvent", back_populates="template", cascade="all, delete-orphan")


class EmailReadEvent(Base):
    __tablename__ = "email_read_event"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("email_template.id"))
    uuid = Column(String, unique=True, index=True)

    template = relationship("EmailTemplate", back_populates="read_events")


Base.metadata.create_all(bind=engine)
