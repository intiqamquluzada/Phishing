from sqlalchemy import Column, Integer, String
from database import Base, engine

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


Base.metadata.create_all(bind=engine)
