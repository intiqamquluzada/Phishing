from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from phish.database import Base, engine


class TypeOfTraining(PyEnum):
    ADMIN = "ADMIN"
    SIMPLE = "SIMPLE"
    PREMIUM = "PREMIUM"


class TrainingInformation(Base):
    __tablename__ = 'TrainingInformation'

    id = Column(Integer, primary_key=True, index=True)
    question_count = Column(Integer)
    pages_count = Column(Integer)
    type = Column(String, nullable=False)

    trainings = relationship("Training", back_populates="info")


class Training(Base):
    __tablename__ = 'Training'

    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String)
    passing_score = Column(Integer)
    training_information = Column(Integer, ForeignKey("TrainingInformation.id"))
    preview = Column(String)
    compliance = Column(Boolean, default=False)

    info = relationship("TrainingInformation", back_populates="trainings")


Base.metadata.create_all(bind=engine)
