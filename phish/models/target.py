from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from phish.database import Base, engine


class TargetUser(Base):
    __tablename__ = 'TargetUser'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    company = Column(String)
    job_title = Column(String)
    targets = relationship("Target", back_populates="target_user")


class Target(Base):
    __tablename__ = 'Target'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    target_user_id = Column(Integer, ForeignKey("TargetUser.id"))
    target_user = relationship("TargetUser", back_populates="targets")


Base.metadata.create_all(bind=engine)
