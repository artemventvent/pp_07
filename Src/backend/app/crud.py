from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from . import models, schemas, auth

logger = logging.getLogger(__name__)


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role_id=user.role_id,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = auth.get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, role_name: str) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.role_name == role_name).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
    return db.query(models.Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: schemas.RoleCreate) -> models.Role:
    db_role = models.Role(
        role_name=role.role_name,
        description=role.description,
        permissions=role.permissions
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role_update: schemas.RoleUpdate) -> Optional[models.Role]:
    db_role = get_role(db, role_id)
    if db_role:
        update_data = role_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
    
    return db_role


def delete_role(db: Session, role_id: int) -> bool:
    db_role = get_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False


def get_product_type(db: Session, type_id: int) -> Optional[models.ProductType]:
    return db.query(models.ProductType).filter(models.ProductType.id == type_id).first()


def get_product_types(db: Session, skip: int = 0, limit: int = 100) -> List[models.ProductType]:
    return db.query(models.ProductType).offset(skip).limit(limit).all()


def create_product_type(db: Session, product_type: schemas.ProductTypeCreate) -> models.ProductType:
    db_product_type = models.ProductType(**product_type.model_dump())
    db.add(db_product_type)
    db.commit()
    db.refresh(db_product_type)
    return db_product_type


def update_product_type(db: Session, type_id: int, product_type_update: schemas.ProductTypeUpdate) -> Optional[models.ProductType]:
    db_product_type = get_product_type(db, type_id)
    if db_product_type:
        update_data = product_type_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product_type, field, value)
        
        db_product_type.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_product_type)
    
    return db_product_type


def delete_product_type(db: Session, type_id: int) -> bool:
    db_product_type = get_product_type(db, type_id)
    if db_product_type:
        db.delete(db_product_type)
        db.commit()
        return True
    return False


def get_batch(db: Session, batch_id: int) -> Optional[models.ProductionBatch]:
    return db.query(models.ProductionBatch).filter(models.ProductionBatch.id == batch_id).first()


def get_batch_by_number(db: Session, batch_number: str) -> Optional[models.ProductionBatch]:
    return db.query(models.ProductionBatch).filter(models.ProductionBatch.batch_number == batch_number).first()


def get_batches(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    product_type_id: Optional[int] = None
) -> List[models.ProductionBatch]:
    query = db.query(models.ProductionBatch)
    
    if status:
        query = query.filter(models.ProductionBatch.status == status)
    if product_type_id:
        query = query.filter(models.ProductionBatch.product_type_id == product_type_id)
    
    return query.offset(skip).limit(limit).all()


def create_batch(db: Session, batch: schemas.ProductionBatchCreate) -> models.ProductionBatch:
    db_batch = models.ProductionBatch(**batch.model_dump())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def update_batch(db: Session, batch_id: int, batch_update: schemas.ProductionBatchUpdate) -> Optional[models.ProductionBatch]:
    db_batch = get_batch(db, batch_id)
    if db_batch:
        update_data = batch_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_batch, field, value)
        
        db_batch.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_batch)
    
    return db_batch


def delete_batch(db: Session, batch_id: int) -> bool:
    db_batch = get_batch(db, batch_id)
    if db_batch:
        db.delete(db_batch)
        db.commit()
        return True
    return False

def create_inspection_result(db: Session, inspection: schemas.InspectionResultCreate) -> models.InspectionResult:
    db_inspection = models.InspectionResult(**inspection.model_dump())
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


def get_inspection_results(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    verdict: Optional[str] = None
) -> List[models.InspectionResult]:
    query = db.query(models.InspectionResult)
    
    if batch_id:
        query = query.filter(models.InspectionResult.batch_id == batch_id)
    if verdict:
        query = query.filter(models.InspectionResult.overall_verdict == verdict)
    
    return query.offset(skip).limit(limit).all()

def get_inspection_result(db: Session, inspection_id: int) -> Optional[models.InspectionResult]:
    return db.query(models.InspectionResult).filter(models.InspectionResult.id == inspection_id).first()


def update_inspection_result(db: Session, inspection_id: int, inspection_update: schemas.InspectionResultUpdate) -> Optional[models.InspectionResult]:
    db_inspection = get_inspection_result(db, inspection_id)
    if db_inspection:
        update_data = inspection_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_inspection, field, value)
        
        db_inspection.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_inspection)
    
    return db_inspection


def delete_inspection_result(db: Session, inspection_id: int) -> bool:
    db_inspection = get_inspection_result(db, inspection_id)
    if db_inspection:
        db.delete(db_inspection)
        db.commit()
        return True
    return False


def get_defect_type(db: Session, defect_type_id: int) -> Optional[models.DefectType]:
    return db.query(models.DefectType).filter(models.DefectType.id == defect_type_id).first()


def get_defect_types(db: Session, skip: int = 0, limit: int = 100) -> List[models.DefectType]:
    return db.query(models.DefectType).offset(skip).limit(limit).all()


def create_defect_type(db: Session, defect_type: schemas.DefectTypeCreate) -> models.DefectType:
    db_defect_type = models.DefectType(**defect_type.model_dump())
    db.add(db_defect_type)
    db.commit()
    db.refresh(db_defect_type)
    return db_defect_type


def update_defect_type(db: Session, defect_type_id: int, defect_type_update: schemas.DefectTypeUpdate) -> Optional[models.DefectType]:
    db_defect_type = get_defect_type(db, defect_type_id)
    if db_defect_type:
        update_data = defect_type_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_defect_type, field, value)
        
        db.commit()
        db.refresh(db_defect_type)
    
    return db_defect_type


def delete_defect_type(db: Session, defect_type_id: int) -> bool:
    db_defect_type = get_defect_type(db, defect_type_id)
    if db_defect_type:
        db.delete(db_defect_type)
        db.commit()
        return True
    return False