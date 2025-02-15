from sqlalchemy import (Column, Integer, String, Enum,
                        ForeignKey, UniqueConstraint,
                        Boolean)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from database import Base, engine
from models.role import Role


class RoleType(PyEnum):
    ADMIN = "ADMIN"
    SIMULATOR = "SIMULATOR"
    USER = "USER"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True)
    hashed_password = Column(String(150))
    verification_code = Column(String(150))

    # MFA-related fields
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(150), nullable=True)
    mfa_backup_codes = Column(String(150), nullable=True)

    role_id = Column(Integer, ForeignKey("role.id"))
    role = relationship("Role", back_populates="users")

    company_id = Column(Integer, ForeignKey("company.id"))
    company = relationship("Company", back_populates="users")

    administration = relationship("Administration", back_populates="user", uselist=False)
    invite = relationship("Invite", back_populates="user", uselist=False)


