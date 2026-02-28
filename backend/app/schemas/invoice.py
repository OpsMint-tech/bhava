from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class KeyValue(BaseModel):
    key: str
    value: Any

class Page(BaseModel):
    number: int
    page_type: str
    key_values: Dict[str, Any]
    items: List[List[KeyValue]]

class InvoiceResponse(BaseModel):
    id: int
    name: str
    created_by: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    # status: initiated, parsed, completed, failed
    status: str
    num_pages: Optional[int] = None
    pages: Optional[List[Page]] = None
    extracted_data: Optional[Dict[str, Any]] = None
    reference_data: Optional[Dict[str, Any]] = None
    reviewed: bool = False
    comparison: Optional[Dict[str, Any]] = None  # Now a dict with invoice_details and comparison_results
    error_message: Optional[str] = None

class InvoiceUpload(BaseModel):
    id: int
    status: str
    message: str

class DocumentSummary(BaseModel):
    id: int
    name: str
    created_by: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    # status: initiated, parsed, completed, failed
    status: str
    num_pages: int
    extracted_data: Optional[Dict[str, Any]] = None
    reference_data: Optional[Dict[str, Any]] = None
    comparison: Optional[Dict[str, Any]] = None  # Now a dict with invoice_details and comparison_results
    reviewed: bool

class InvoiceList(BaseModel):
    total: int
    page: int
    limit: int
    documents: List[DocumentSummary] 