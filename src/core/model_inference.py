import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Union
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, scoped_session
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
import uuid

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base declarative class for SQLAlchemy
Base = declarative_base()

# Database connection setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/federated_learning")
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Utility function for generating UUIDs
def generate_uuid():
    return str(uuid.uuid4())

# Abstract base class for common audit columns
class AuditMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

# Model for storing model metadata and versioning
class ModelMetadata(Base, AuditMixin):
    __tablename__ = "model_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    model_name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    artifact_path = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String(255), nullable=False)

    # Unique constraint to ensure no duplicate model versions
    __table_args__ = (
        UniqueConstraint("model_name", "version", name="uq_model_name_version"),
    )

    def __repr__(self):
        return f"<ModelMetadata(model_name={self.model_name}, version={self.version}, is_active={self.is_active})>"

# Model for storing inference requests and results
class InferenceRequest(Base, AuditMixin):
    __tablename__ = "inference_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    model_id = Column(UUID(as_uuid=True), ForeignKey("model_metadata.id", ondelete="CASCADE"), nullable=False)
    input_data = Column(JSONB, nullable=False)
    output_data = Column(JSONB, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, SUCCESS, FAILED
    error_message = Column(Text, nullable=True)

    # Relationships
    model = relationship("ModelMetadata", back_populates="inference_requests")

    def __repr__(self):
        return f"<InferenceRequest(id={self.id}, model_id={self.model_id}, status={self.status})>"

# Back-populate relationship
ModelMetadata.inference_requests = relationship("InferenceRequest", back_populates="model", cascade="all, delete-orphan")

# Database initialization
def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema created successfully.")

# Inference API logic
class ModelInferenceService:
    def __init__(self):
        self.db = SessionLocal()

    def get_active_model(self, model_name: str) -> ModelMetadata:
        """Fetch the active model for a given model name."""
        model = self.db.query(ModelMetadata).filter(
            ModelMetadata.model_name == model_name,
            ModelMetadata.is_active == True,
            ModelMetadata.deleted_at.is_(None)
        ).first()
        if not model:
            raise ValueError(f"No active model found for name: {model_name}")
        return model

    def create_inference_request(self, model_name: str, input_data: Dict[str, Any]) -> InferenceRequest:
        """Create a new inference request."""
        model = self.get_active_model(model_name)
        inference_request = InferenceRequest(
            model_id=model.id,
            input_data=input_data,
            status="PENDING"
        )
        self.db.add(inference_request)
        self.db.commit()
        self.db.refresh(inference_request)
        return inference_request

    def process_inference_request(self, request_id: str, output_data: Dict[str, Any], error_message: str = None):
        """Update the inference request with results or errors."""
        inference_request = self.db.query(InferenceRequest).filter(
            InferenceRequest.id == request_id,
            InferenceRequest.deleted_at.is_(None)
        ).first()
        if not inference_request:
            raise ValueError(f"Inference request with ID {request_id} not found.")

        if error_message:
            inference_request.status = "FAILED"
            inference_request.error_message = error_message
        else:
            inference_request.status = "SUCCESS"
            inference_request.output_data = output_data

        self.db.commit()
        self.db.refresh(inference_request)
        return inference_request

    def batch_inference(self, model_name: str, batch_inputs: List[Dict[str, Any]]) -> List[InferenceRequest]:
        """Process batch inference requests."""
        model = self.get_active_model(model_name)
        inference_requests = []
        for input_data in batch_inputs:
            inference_request = InferenceRequest(
                model_id=model.id,
                input_data=input_data,
                status="PENDING"
            )
            self.db.add(inference_request)
            inference_requests.append(inference_request)

        self.db.commit()
        for request in inference_requests:
            self.db.refresh(request)
        return inference_requests

# Example usage
if __name__ == "__main__":
    init_db()  # Initialize the database schema

    service = ModelInferenceService()

    # Example: Create a new inference request
    try:
        request = service.create_inference_request(
            model_name="diabetes_prediction",
            input_data={"age": 45, "bmi": 28.7, "glucose_level": 120}
        )
        logger.info(f"Inference request created: {request}")
    except Exception as e:
        logger.error(f"Error creating inference request: {e}")