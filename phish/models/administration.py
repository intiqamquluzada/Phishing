from sqlalchemy import (Column, Integer, String, Boolean, Enum, ForeignKey)
from sqlalchemy.orm import relationship
from phish.database import Base, engine
from phish.models.users import User
from phish.models.campaign import Campaign
from enum import Enum as PyEnum


class Status(PyEnum):
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"


class Administration(Base):
    __tablename__ = "administration"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String)
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
    verification_code = Column(String)



Base.metadata.create_all(bind=engine)
