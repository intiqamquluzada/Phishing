from sqlalchemy import Column, Integer, String, Enum
from enum import Enum as PyEnum
from phish.database import Base, engine


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
    subject = Column(String)
    body = Column(String)


Base.metadata.create_all(bind=engine)
