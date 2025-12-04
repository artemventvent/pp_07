from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.ProductType])
def read_product_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить список типов продукции"""
    product_types = crud.get_product_types(db, skip=skip, limit=limit)
    return product_types


@router.post("/", response_model=schemas.ProductType, status_code=status.HTTP_201_CREATED)
def create_product_type(
    product_type: schemas.ProductTypeCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Создать новый тип продукции"""
    # Только админ и менеджер качества могут создавать типы продукции
    if not (current_user.role and (current_user.role.permissions.get("admin") or 
                                   current_user.role.role_name == "quality_manager")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Добавляем ID создателя
    product_type.created_by = current_user.id
    
    return crud.create_product_type(db=db, product_type=product_type)


@router.get("/{type_id}", response_model=schemas.ProductType)
def read_product_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить тип продукции по ID"""
    db_product_type = crud.get_product_type(db, type_id=type_id)
    if db_product_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product type not found"
        )
    return db_product_type


@router.put("/{type_id}", response_model=schemas.ProductType)
def update_product_type(
    type_id: int,
    product_type_update: schemas.ProductTypeUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Обновить тип продукции"""
    if not (current_user.role and (current_user.role.permissions.get("admin") or 
                                   current_user.role.role_name == "quality_manager")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_product_type = crud.update_product_type(db, type_id=type_id, product_type_update=product_type_update)
    if db_product_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product type not found"
        )
    return db_product_type


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Удалить тип продукции"""
    if not (current_user.role and current_user.role.permissions.get("admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not crud.delete_product_type(db, type_id=type_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product type not found"
        )