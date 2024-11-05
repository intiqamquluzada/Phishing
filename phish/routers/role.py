from sqlalchemy.orm import Session

from fastapi import (APIRouter, Depends, HTTPException, Form,
                     UploadFile, File, Request, Query)
from fastapi.responses import JSONResponse
from phish.dependencies import get_db
from enum import Enum as PyEnum
from typing import Dict, Any
from phish.schemas.role import RoleBase, RoleResponse, Permission, RolePatch, RoleListResponse
from phish.models.role import Role
from phish.models.users import User
from typing import List


router = APIRouter(
    prefix="/roles",
    tags=['Roles']
)


@router.get("/",
            response_model=RoleListResponse,
            summary="List of Roles",
            description="List of Roles")
async def role_list(db: Session = Depends(get_db),
                    limit: int = Query(10, description="Number of roles to retrieve"),
                    offset: int = Query(0, description="Offset from the start")):
    query = db.query(Role)
    total_roles = query.count()
    roles = query.offset(offset).limit(limit).all()

    if not roles:
        raise HTTPException(status_code=404, detail="Roles not found")

    roles_response = []
    for role in roles:
        roles_response.append(
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                permissions=role.get_permission()  # Extract permissions correctly
            )
        )

    return RoleListResponse(roles=roles_response, total_roles=total_roles)




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
    role = db.query(Role).filter(Role.id==role_id).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Role successfully removed"})
