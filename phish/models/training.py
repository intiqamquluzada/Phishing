from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from database import Base, engine


class TypeOfTraining(PyEnum):
    ADMIN = "ADMIN"
    SIMPLE = "SIMPLE"
    PREMIUM = "PREMIUM"


class Question(Base):
    __tablename__ = 'Question'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(150))
    training_information_id = Column(Integer, ForeignKey("TrainingInformation.id"))
    training_information = relationship("TrainingInformation", back_populates="question")


class TrainingInformation(Base):
    __tablename__ = 'TrainingInformation'

    id = Column(Integer, primary_key=True, index=True)
    question_count = Column(Integer)
    pages_count = Column(Integer)

    trainings = relationship("Training", back_populates="info")
    question = relationship("Question", back_populates="training_information")


class Training(Base):
    __tablename__ = 'Training'

    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(150))
    passing_score = Column(Integer)
    training_information = Column(Integer, ForeignKey("TrainingInformation.id"))
    presentation = Column(String(150))
    preview = Column(String(150))


    info = relationship("TrainingInformation", back_populates="trainings")


