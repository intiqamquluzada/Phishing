from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, engine


class TargetUser(Base):
    __tablename__ = 'target_user'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    job_title = Column(String(150))
    company = Column(String(150), nullable=False)
    target_id = Column(Integer, ForeignKey("target.id")) 
    target = relationship("Target", back_populates="target_users")


class Target(Base):
    __tablename__ = 'target'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))

    # target_user_id = Column(Integer, ForeignKey("target_user.id"))
    target_users = relationship("TargetUser", back_populates="target")


