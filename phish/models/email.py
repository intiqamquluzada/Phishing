from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

from phish.database import Base, engine


class EmailTemplate(Base):
    __tablename__ = 'EmailTemplate'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    difficulty = Column(String, nullable=False)
    subject = Column(String)
    body = Column(String)
    file_path = Column(String, nullable=False)

    read_events = relationship("EmailReadEvent", back_populates="template", cascade="all, delete-orphan")



class EmailReadEvent(Base):
    __tablename__ = "email_read_event"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey('EmailTemplate.id'))
    uuid = Column(String, unique=True, index=True)

    template = relationship("EmailTemplate", back_populates="read_events")


Base.metadata.create_all(bind=engine)
