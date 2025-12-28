from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from app.db.base_class import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    # status: initiated, parsed, completed, failed
    status = Column(String(50), nullable=False, default="initiated")
    num_pages = Column(Integer, nullable=True)
    pages = Column(JSON, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    reference_data = Column(JSON, nullable=True)
    reviewed = Column(Boolean, default=False)
    comparison = Column(JSON, nullable=True)  # Renamed from discrepancies
    error_message = Column(Text, nullable=True) 