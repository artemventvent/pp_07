from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric, Date, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default={"read": True, "write": False, "delete": False, "admin": False})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(200))
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    role = relationship("Role", back_populates="users")
    batches_created = relationship("ProductionBatch", foreign_keys="[ProductionBatch.created_by]", back_populates="creator")
    inspections = relationship("InspectionResult", back_populates="inspector")


class ProductType(Base):
    __tablename__ = "product_types"
    
    id = Column(Integer, primary_key=True, index=True)
    type_code = Column(String(50), unique=True, nullable=False)
    type_name = Column(String(200), nullable=False)
    standard = Column(String(100))
    thickness_range = Column(String(100))
    width_range = Column(String(100))
    material_grade = Column(String(100))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    batches = relationship("ProductionBatch", back_populates="product_type")
    creator = relationship("User", foreign_keys=[created_by])


class ProductionBatch(Base):
    __tablename__ = "production_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(100), unique=True, nullable=False, index=True)
    product_type_id = Column(Integer, ForeignKey("product_types.id", ondelete="RESTRICT"), nullable=False)
    production_date = Column(Date, nullable=False)
    furnace_number = Column(String(50))
    shift_number = Column(Integer)
    total_weight_kg = Column(Numeric(10, 2))
    total_length_m = Column(Numeric(10, 2))
    status = Column(String(50), default="в производстве")
    quality_rating = Column(Integer)
    metadata = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    product_type = relationship("ProductType", back_populates="batches")
    creator = relationship("User", foreign_keys=[created_by])
    inspection_results = relationship("InspectionResult", back_populates="batch", cascade="all, delete-orphan")


class DefectType(Base):
    __tablename__ = "defect_types"
    
    id = Column(Integer, primary_key=True, index=True)
    defect_code = Column(String(50), unique=True, nullable=False)
    defect_name = Column(String(200), nullable=False)
    category = Column(String(100))
    severity_level = Column(String(50))
    description = Column(Text)
    measurement_unit = Column(String(50))
    threshold_value = Column(Numeric(10, 4))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    defect_details = relationship("DefectDetail", back_populates="defect_type")
    creator = relationship("User", foreign_keys=[created_by])


class InspectionPoint(Base):
    __tablename__ = "inspection_points"
    
    id = Column(Integer, primary_key=True, index=True)
    point_name = Column(String(200), nullable=False)
    point_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    equipment_type = Column(String(100))
    location_in_line = Column(String(100))
    coordinates = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InspectionResult(Base):
    __tablename__ = "inspection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("production_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    inspection_point_id = Column(Integer, ForeignKey("inspection_points.id"))
    inspection_time = Column(DateTime(timezone=True), server_default=func.now())
    inspector_id = Column(Integer, ForeignKey("users.id"))
    inspector_name = Column(String(200))
    measurement_data = Column(JSON, nullable=False)
    is_defect_detected = Column(Boolean, default=False)
    defect_count = Column(Integer, default=0)
    overall_verdict = Column(String(50), default="соответствует")
    status = Column(String(50), default="обработка")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    batch = relationship("ProductionBatch", back_populates="inspection_results")
    inspection_point = relationship("InspectionPoint")
    inspector = relationship("User", back_populates="inspections")
    defect_details = relationship("DefectDetail", back_populates="inspection_result", cascade="all, delete-orphan")


class DefectDetail(Base):
    __tablename__ = "defect_details"
    
    id = Column(Integer, primary_key=True, index=True)
    inspection_result_id = Column(Integer, ForeignKey("inspection_results.id", ondelete="CASCADE"), nullable=False, index=True)
    defect_type_id = Column(Integer, ForeignKey("defect_types.id"), nullable=False, index=True)
    defect_location = Column(JSON)
    severity = Column(Numeric(5, 2))
    size_mm = Column(Numeric(10, 2))
    image_path = Column(String(500))
    is_repaired = Column(Boolean, default=False)
    repair_method = Column(String(200))
    repair_date = Column(DateTime(timezone=True))
    repair_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    inspection_result = relationship("InspectionResult", back_populates="defect_details")
    defect_type = relationship("DefectType", back_populates="defect_details")