from sqlalchemy import Column, Integer, String, Enum
from enum import Enum as PyEnum
from phish.database import Base, engine


class EmailType(PyEnum):
    STANDARD = "STANDARD"
    CONVERSATIONAL = "CONVERSATIONAL"


class EmailDifficulty(PyEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class EmailTemplate(Base):
    __tablename__ = 'EmailTemplate'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    difficulty = Column(String, nullable=False)
    type = Column(String, nullable=False)
    payload_type = Column(String)
    subject = Column(String)
    body = Column(String)


Base.metadata.create_all(bind=engine)
