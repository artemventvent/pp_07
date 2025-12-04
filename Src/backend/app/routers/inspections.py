from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.InspectionResult])
def read_inspections(
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    verdict: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить список результатов контроля"""
    inspections = crud.get_inspection_results(
        db, 
        skip=skip, 
        limit=limit,
        batch_id=batch_id,
        verdict=verdict
    )
    return inspections


@router.post("/", response_model=schemas.InspectionResult, status_code=status.HTTP_201_CREATED)
def create_inspection(
    inspection: schemas.InspectionResultCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Создать новый результат контроля"""
    # Оператор и выше могут создавать результаты контроля
    if not (current_user.role and (current_user.role.permissions.get("write") or 
                                   current_user.role.permissions.get("admin"))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Добавляем inspector_id если не указан
    if not inspection.inspector_id:
        inspection.inspector_id = current_user.id
    
    if not inspection.inspector_name:
        inspection.inspector_name = current_user.full_name or current_user.username
    
    return crud.create_inspection_result(db=db, inspection=inspection)


@router.get("/{inspection_id}", response_model=schemas.InspectionResult)
def read_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Получить результат контроля по ID"""
    # Нужно реализовать функцию get_inspection_result в crud.py
    from ..crud import get_inspection_result
    db_inspection = get_inspection_result(db, inspection_id=inspection_id)
    if db_inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection result not found"
        )
    return db_inspection


@router.put("/{inspection_id}", response_model=schemas.InspectionResult)
def update_inspection(
    inspection_id: int,
    inspection_update: schemas.InspectionResultUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Обновить результат контроля"""
    if not (current_user.role and (current_user.role.permissions.get("write") or 
                                   current_user.role.permissions.get("admin"))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Нужно реализовать функцию update_inspection_result в crud.py
    from ..crud import update_inspection_result
    db_inspection = update_inspection_result(db, inspection_id=inspection_id, inspection_update=inspection_update)
    if db_inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection result not found"
        )
    return db_inspection


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Удалить результат контроля"""
    if not (current_user.role and current_user.role.permissions.get("delete")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Нужно реализовать функцию delete_inspection_result в crud.py
    from ..crud import delete_inspection_result
    if not delete_inspection_result(db, inspection_id=inspection_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection result not found"
        )