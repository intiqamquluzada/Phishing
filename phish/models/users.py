from sqlalchemy import (Column, Integer, String, Enum,
                        ForeignKey, UniqueConstraint,
                        Boolean)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from phish.database import Base, engine


class RoleType(PyEnum):
    ADMIN = "ADMIN"
    SIMULATOR = "SIMULATOR"
    USER = "USER"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    verification_code = Column(String)
    role = Column(Enum(RoleType), nullable=False)
    administration = relationship("Administration", back_populates="user", foreign_keys="[Administration.user_id]")
    invite = relationship("Invite", back_populates="user", foreign_keys="[Invite.user_id]")

Base.metadata.create_all(bind=engine)
