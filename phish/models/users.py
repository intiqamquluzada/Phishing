from sqlalchemy import Column, Integer, String, Enum
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


Base.metadata.create_all(bind=engine)
