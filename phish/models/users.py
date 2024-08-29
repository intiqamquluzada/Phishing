from sqlalchemy import Column, Integer, String
from db_config.database import Base


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


Base.metadata.create_all(bin=engine)

