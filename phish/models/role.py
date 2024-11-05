from sqlalchemy import (Column, Integer, String, Boolean,
                        Enum, ForeignKey, DateTime, func)
from sqlalchemy.orm import relationship
from phish.database import Base, engine
from typing import List


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    permission = Column(String)
    users = relationship("User", back_populates="role")
    created_at = Column(DateTime, server_default=func.now())

    def set_permissions(self, permissions: List[str]):
        self.permission = ','.join(permissions)

    def get_permission(self):
        return self.permission.split(',') if self.permission else []


Base.metadata.create_all(bind=engine)
