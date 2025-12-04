from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.ProductionBatch])
def read_batches(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    product_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить список производственных партий"""
    batches = crud.get_batches(
        db, 
        skip=skip, 
        limit=limit, 
        status=status,
        product_type_id=product_type_id
    )
    return batches


@router.post("/", response_model=schemas.ProductionBatch, status_code=status.HTTP_201_CREATED)
def create_batch(
    batch: schemas.ProductionBatchCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Создать новую производственную партию"""
    if not (current_user.role and (current_user.role.permissions.get("write") or 
                                   current_user.role.permissions.get("admin"))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_batch = crud.get_batch_by_number(db, batch_number=batch.batch_number)
    if db_batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch number already exists"
        )
    
    batch.created_by = current_user.id
    
    return crud.create_batch(db=db, batch=batch)


@router.get("/{batch_id}", response_model=schemas.ProductionBatch)
def read_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить партию по ID"""
    db_batch = crud.get_batch(db, batch_id=batch_id)
    if db_batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    return db_batch


@router.put("/{batch_id}", response_model=schemas.ProductionBatch)
def update_batch(
    batch_id: int,
    batch_update: schemas.ProductionBatchUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Обновить партию"""
    if not (current_user.role and (current_user.role.permissions.get("write") or 
                                   current_user.role.permissions.get("admin"))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_batch = crud.update_batch(db, batch_id=batch_id, batch_update=batch_update)
    if db_batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    return db_batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Удалить партию"""
    if not (current_user.role and current_user.role.permissions.get("delete")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not crud.delete_batch(db, batch_id=batch_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )