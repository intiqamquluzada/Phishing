from sqlalchemy import (Column, Integer, String, Boolean, Enum, ForeignKey)
from sqlalchemy.orm import relationship
from phish.database import Base, engine


class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    # administration = relationship("Administration", back_populates="campaign", foreign_keys="[Administration.campaign_id]")
    # invite = relationship("Invite", back_populates="campaign", foreign_keys="[Invite.campaign_id]")


Base.metadata.create_all(bind=engine)
