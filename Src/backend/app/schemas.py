from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# Базовые схемы
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserInDB(User):
    hashed_password: str


# Role schemas
class RoleBase(BaseSchema):
    role_name: str
    description: Optional[str] = None
    permissions: Dict[str, Any] = {"read": True, "write": False, "delete": False, "admin": False}


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseSchema):
    role_name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None


class Role(RoleBase):
    id: int
    created_at: datetime


# ProductType schemas
class ProductTypeBase(BaseSchema):
    type_code: str
    type_name: str
    standard: Optional[str] = None
    thickness_range: Optional[str] = None
    width_range: Optional[str] = None
    material_grade: Optional[str] = None
    description: Optional[str] = None


class ProductTypeCreate(ProductTypeBase):
    created_by: Optional[int] = None


class ProductTypeUpdate(BaseSchema):
    type_name: Optional[str] = None
    standard: Optional[str] = None
    thickness_range: Optional[str] = None
    width_range: Optional[str] = None
    material_grade: Optional[str] = None
    description: Optional[str] = None


class ProductType(ProductTypeBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# ProductionBatch schemas
class ProductionBatchBase(BaseSchema):
    batch_number: str
    product_type_id: int
    production_date: date
    furnace_number: Optional[str] = None
    shift_number: Optional[int] = None
    total_weight_kg: Optional[Decimal] = None
    total_length_m: Optional[Decimal] = None
    status: str = "в производстве"
    quality_rating: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductionBatchCreate(ProductionBatchBase):
    created_by: Optional[int] = None


class ProductionBatchUpdate(BaseSchema):
    furnace_number: Optional[str] = None
    shift_number: Optional[int] = None
    total_weight_kg: Optional[Decimal] = None
    total_length_m: Optional[Decimal] = None
    status: Optional[str] = None
    quality_rating: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductionBatch(ProductionBatchBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Вложенные объекты
    product_type: Optional[ProductType] = None


# InspectionResult schemas
class InspectionResultBase(BaseSchema):
    batch_id: int
    inspection_point_id: Optional[int] = None
    inspector_id: Optional[int] = None
    inspector_name: Optional[str] = None
    measurement_data: Dict[str, Any]
    overall_verdict: str = "соответствует"
    status: str = "обработка"
    notes: Optional[str] = None


class InspectionResultCreate(InspectionResultBase):
    pass


class InspectionResultUpdate(BaseSchema):
    overall_verdict: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class InspectionResult(InspectionResultBase):
    id: int
    inspection_time: datetime
    is_defect_detected: bool = False
    defect_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    # Вложенные объекты
    batch: Optional[ProductionBatch] = None


# Token and Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str