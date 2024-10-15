from sqlalchemy.orm import Session
from fastapi import (APIRouter, Depends, HTTPException, Form,
                     UploadFile, File, Request)
from fastapi.responses import JSONResponse
from phish.dependencies import get_db
from enum import Enum as PyEnum
from phish.schemas.role import RoleBase, RoleResponse, Permission, RolePatch
from phish.models.role import Role
from phish.models.users import User
from typing import List


router = APIRouter(
    prefix="/roles",
    tags=['Roles']
)


@router.get("/",
            response_model=List[RoleResponse],
            summary="List of Role",
            description="List of Role")
async def role_list(db: Session = Depends(get_db)):
    roles = db.query(Role).all()

    if not roles:
        raise HTTPException(status_code=404, detail="Role not found")

    return roles


@router.get("/detail/{role_id}",
            response_model=RoleResponse,
            summary="Detail of Role",
            description="Detail of Role")
async def role_list(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return role

@router.get("/permissions",
            summary="List of permission",
            description="List of permission")
async def permission_list():
    return [perm.value for perm in Permission]


@router.post("/create/",
             response_model=RoleResponse,
             summary="Create a Role",
             description="Create a Role")
async def create_role(role: RoleBase, db: Session = Depends(get_db)):
    role_create = Role(
        name=role.name,
        description=role.description,
        user_id=role.user_id,
    )

    role_create.set_permissions([perm.value for perm in role.permission])

    db.add(role_create)
    db.commit()
    db.refresh(role_create)

    return role_create


@router.put("/update/{role_id}",
            response_model=RoleResponse,
            summary="Update role",
            description="Update role")
async def update_role(role_id: int, role_update: RoleBase,
                      db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.user_id = role_update.user_id
    role.name = role_update.name
    role.description = role_update.description

    role.set_permissions([perm.value for perm in role_update.permission])

    db.commit()
    db.refresh(role)

    return role


@router.patch("/update/{role_id}",
              response_model=RoleResponse,
              summary="Update role",
              description="Update role")
async def update_role_patch(role_id: int, role_update: RolePatch,
                            db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role_update.user_id is not None:
        role.user_id = role_update.user_id
    if role_update.name is not None:
        role.name = role_update.name
    if role_update.description is not None:
        role.description = role_update.description

    if len(role_update.permission) > 0:
        role.set_permissions([perm.value for perm in role_update.permission])

    db.commit()
    db.refresh(role)

    return role



@router.delete("/delete/{role_id}",
               summary="Delete role",
               description="Delete role")
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Role successfully removed"})