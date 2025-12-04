from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.Role])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить список ролей"""
    # Только админ может видеть роли
    if not (current_user.role and current_user.role.permissions.get("admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles


@router.post("/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def create_role(
    role: schemas.RoleCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Создать новую роль"""
    if not (current_user.role and current_user.role.permissions.get("admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_role = crud.get_role_by_name(db, role_name=role.role_name)
    if db_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    return crud.create_role(db=db, role=role)


@router.get("/{role_id}", response_model=schemas.Role)
def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить роль по ID"""
    if not (current_user.role and current_user.role.permissions.get("admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return db_role


@router.put("/{role_id}", response_model=schemas.Role)
def update_role(
    role_id: int,
    role_update: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Обновить роль"""
    if not (current_user.role and current_user.role.permissions.get("admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_role = crud.update_role(db, role_id=role_id, role_update=role_update)
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return db_role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Удалить роль"""
    if not (current_user.role and current_user.role.permissions.get("admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not crud.delete_role(db, role_id=role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )