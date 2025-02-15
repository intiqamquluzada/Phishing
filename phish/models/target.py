from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, engine


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(150), nullable=True)

    campaigns = relationship("Campaign", back_populates="company")

    # Separate relationships for User and TargetUser
    users = relationship("User", back_populates="company")  # Relationship for the User model
    target_users = relationship("TargetUser", back_populates="company")


class TargetUser(Base):
    __tablename__ = 'target_user'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    job_title = Column(String(150))

    company_id = Column(Integer, ForeignKey("company.id"))
    company = relationship("Company", back_populates="target_users")  # Match with `Company.target_users`

    targets = relationship("Target", back_populates="target_user")


class Target(Base):
    __tablename__ = 'target'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))

    # Ensure the reverse relationship with TargetUser is defined properly
    target_user_id = Column(Integer, ForeignKey("target_user.id"))
    target_user = relationship("TargetUser", back_populates="targets")


