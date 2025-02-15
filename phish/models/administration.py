from sqlalchemy import (Column, Integer, String, Boolean, Enum, ForeignKey)
from sqlalchemy.orm import relationship
from database import Base, engine
from models.users import User
from models.campaign import Campaign
from enum import Enum as PyEnum


class Status(PyEnum):
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"


class Administration(Base):
    __tablename__ = "administration"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    status = Column(String(150))
    is_active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="administration")


class Invite(Base):
    __tablename__ = "invite"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="invite")
    # campaign_id = Column(Integer, ForeignKey("campaign.id"))
    # campaign = relationship("Campaign", back_populates="invite")
    verification_code = Column(String(150))



