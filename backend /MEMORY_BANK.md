# Neura API - Memory Bank

## System Overview

The Neura API is a comprehensive document processing service built with FastAPI that specializes in invoice processing, OCR extraction, and document classification. The system uses a modular architecture with separate services for different document types and processing tasks.

## Core Architecture

### Technology Stack
- **Framework**: FastAPI with Uvicorn ASGI server
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT-based with OAuth2PasswordBearer
- **OCR**: PaddleOCR, Tesseract, pdf2image
- **LLM**: GitHub Inference API (primary), Ollama (fallback)
- **PDF Processing**: Docling, pdfplumber
- **Image Processing**: OpenCV, Pillow

### Project Structure
```
app/
├── core/           # Configuration and security
├── db/            # Database connection and base classes
├── models/        # SQLAlchemy data models
├── schemas/       # Pydantic request/response models
├── services/      # Business logic services
└── main.py        # FastAPI application (1283 lines)
```

## Key Components

### 1. Main Application (`app/main.py`)
- **Size**: 1283 lines with 25+ API endpoints
- **Features**:
  - Invoice upload and processing
  - OCR extraction for 10+ document types
  - Bank statement processing
  - Document classification
  - Background task processing
  - CORS middleware configuration

### 2. Data Models (`app/models/invoice.py`)
```python
class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="initiated")
    num_pages = Column(Integer, nullable=True)
    pages = Column(JSON, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    reference_data = Column(JSON, nullable=True)
    reviewed = Column(Boolean, default=False)
    comparison = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
```

### 3. Service Modules

#### Invoice Processor (`app/services/invoice_processor.py`)
- **Purpose**: Core invoice processing with OCR and LLM extraction
- **Features**:
  - PDF to image conversion
  - OCR text extraction using Tesseract
  - LLM-powered structured data extraction
  - Support for PDF, JPEG, PNG formats
  - Structured invoice data extraction with predefined schema

#### LLM Service (`app/services/llm_service.py`)
- **Purpose**: LLM integration for data comparison and extraction
- **Features**:
  - GitHub Inference API integration
  - Invoice data comparison with reference data
  - Structured JSON response generation
  - Error handling and response validation
  - Template-based comparison analysis

#### OCR Extractor (`app/services/ocr_extractor.py`)
- **Purpose**: Multi-format document OCR extraction
- **Features**:
  - Support for 10+ Indian document types
  - Auto-detection of document types
  - Base64, URL, and file upload support
  - PaddleOCR integration for better accuracy
  - Multi-page document processing
  - Document classification capabilities

**Supported Document Types**:
- `ind_pan` - Individual PAN card
- `comp_pan` - Company PAN card
- `ind_aadhaar` - Aadhaar card
- `ind_voterid` - Voter ID
- `ind_driving_license` - Driving License
- `ind_cheque` - Cancelled Cheque
- `ind_gst_certificate` - GST Certificate
- `ind_udyog_aadhaar` - Udyog Aadhaar
- `ind_electricity_bill` - Electricity Bill
- `water_bill` - Water Bill
- `validate_bank_account` - Penny Drop validation
- `business_card` - Business Card
- `name_board` - Name Board/Signboard
- `rental_agreement` - Rental Agreement
- `property_tax` - Property Tax Document
- `shop_license` - Shop License Certificate (multilingual/handwritten)
- `financial_statement` - Financial Statement (ITR-5 attachment)
- `payslip` - Employee Payslip
- `form16` - Form 16 (Part A and Part B)

- `gst_return` - GST Return (GSTR-1, GSTR-3B, etc.)
- `itr` - Income Tax Return (ITR) documents
- `multi_document` - Multi-document detection and extraction
- `classify` - Document classification

#### PDF Table Extractor (`app/services/pdf_table_extractor.py`)
- **Purpose**: Bank statement and table extraction
- **Features**:
  - PDF to Markdown conversion using Docling
  - Table extraction and JSON conversion
  - Sensitive data extraction (account numbers, PAN, etc.)
  - Local JSON storage for analysis
  - Filtering and regression capabilities

#### Bank Statement Service (`app/services/bank_statement.py`)
- **Purpose**: Dedicated bank statement processing API
- **Features**:
  - PDF to Markdown conversion
  - Markdown to JSON conversion
  - Transaction data extraction
  - File management and cleanup
  - Health check endpoints

#### Form 16 Processing
- **Purpose**: Comprehensive Form 16 extraction (both Part A and Part B)
- **Features**:
  - Employee details extraction (name, PAN, address)
  - Employer details extraction (name, PAN, TAN, address, phone, email)
  - Assessment year and employment period extraction
  - Quarterly summary extraction (Q1-Q4 with receipt numbers and amounts)
  - Book adjustment deposits with detailed transaction information
  - Certificate information including declarant details and verification
  - CIT TDS office information
  - Notes and additional information extraction
  - Multi-page document support with intelligent merging
  - Support for PDF, JPEG, PNG formats
  - Base64 and URL input support

#### GST Return Processing
- **Purpose**: Comprehensive GST Return extraction (GSTR-1, GSTR-3B, etc.)
- **Features**:
  - Taxpayer information extraction (GSTIN, legal name, trade name, financial year)
  - Filing details extraction (GSTR-1, GSTR-1A, GSTR-2B, GSTR-3B dates)
  - Outward supplies breakdown (taxable, zero-rated, nil/exempted, reverse charge)
  - Supplies under section 9(5) extraction
  - Inter-state supplies breakup (unregistered, composition, UIN holders)
  - Input Tax Credit (ITC) details (available, reversed, net, ineligible)
  - Interest details for all tax components
  - Tax period and financial year extraction
  - Multi-page document support with intelligent merging
  - Support for PDF, JPEG, PNG formats
  - Base64 and URL input support

#### ITR Processing
- **Purpose**: Comprehensive Income Tax Return (ITR) extraction
- **Features**:
  - ITR acknowledgement details (acknowledgement number, assessment year, form number, filing section, status)
  - Taxpayer information extraction (PAN, name, complete address breakdown)
  - Income tax calculations (book profit under MAT, business loss, net tax payable, interest and fees)
  - Tax payment details (taxes paid, refund/payable amounts, total income)
  - Dividend distribution tax details
  - Accreted income and tax information (Section 115TD, 115TE)
  - Verification details (verified by, verification method, DSC details, IP address, verification date, DSC ID)
  - Submission details (submission IP, submission date, electronic submission status)
  - Sensitive data classification (identifiers, financial data, personal data)
  - Multi-page document support with intelligent merging
  - Support for PDF, JPEG, PNG formats
  - Base64 and URL input support

#### Multi-Document Processing
- **Purpose**: Comprehensive multi-document detection and extraction from single PDF
- **Features**:
  - Automatic detection of all document types in a single PDF
  - Support for 20+ document types: PAN, Aadhaar, Voter ID, Driving License, Cheque, GST Certificate, Udyog Aadhaar, Electricity Bill, Water Bill, Business Card, Name Board, Rental Agreement, Property Tax, Shop License, Financial Statement, Payslip, Form 16, GST Return, ITR
  - Confidence scoring for each document detection (0.0 to 1.0)
  - Page number tracking for each document found
  - Comprehensive data extraction for each document type
  - Summary statistics (total documents found, document types, pages processed, extraction confidence)
  - Multi-page document support with intelligent merging
  - Support for PDF, JPEG, PNG formats
  - Base64 and URL input support
  - Structured JSON output with detected documents array and summary

### 4. Database Configuration

#### Database Connection (`app/db/session.py`)
```python
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

#### Configuration (`app/core/config.py`)
- Environment variable management
- Database connection strings
- Security settings
- File upload limits
- LLM API configuration

### 5. Security Implementation

#### Authentication (`app/core/security.py`)
- JWT token creation and validation
- OAuth2PasswordBearer integration
- Token expiration handling
- User validation (currently mock implementation)

## API Endpoints Overview

### Invoice Processing
- `POST /api/v1/upload` - Upload invoice with optional reference data
- `GET /api/v1/results/{document_id}` - Get processing results
- `GET /api/v1/documents` - List all documents with filtering

### OCR Extraction
- `POST /api/v1/ocr/extract/pan` - Extract PAN card data
- `POST /api/v1/ocr/extract/ind_aadhaar` - Extract Aadhaar data
- `POST /api/v1/ocr/extract/gst` - Extract GST certificate data
- `POST /api/v1/ocr/extract/cheque` - Extract cancelled cheque data
- `POST /api/v1/ocr/extract/voterid` - Extract Voter ID data
- `POST /api/v1/ocr/extract/ebbill` - Extract electricity bill data
- `POST /api/v1/ocr/extract/driving_license` - Extract driving license data
- `POST /api/v1/ocr/extract/udyog_aadhaar` - Extract Udyog Aadhaar data
- `POST /api/v1/ocr/extract/penny_drop` - Extract penny drop validation data
- `POST /api/v1/ocr/extract/classify` - Classify document type
- `POST /api/v1/ocr/extract/waterbill` - Extract water bill data
 - `POST /api/v1/ocr/extract/business_card` - Extract business card data
 - `POST /api/v1/ocr/extract/name_board` - Extract name board/signboard data
 - `POST /api/v1/ocr/extract/rental_agreement` - Extract rental agreement data
 - `POST /api/v1/ocr/extract/property_tax` - Extract property tax data
- `POST /api/v1/ocr/extract/shop_license` - Extract shop license certificate data
- `POST /api/v1/ocr/extract/financial_statement` - Extract financial statement (ITR-5) data
- `POST /api/v1/ocr/extract/form16` - Extract Form 16 (Part A and Part B) data
- `POST /api/v1/ocr/extract/gst_return` - Extract GST Return (GSTR-1, GSTR-3B, etc.) data
- `POST /api/v1/ocr/extract/itr` - Extract Income Tax Return (ITR) data
- `POST /api/v1/ocr/extract/multi_document` - Multi-document detection and extraction

### Bank Statement Processing
- `POST /api/v1/bank-statement/process` - Process bank statement PDF
- `GET /api/v1/bank-statement/health` - Health check

## Data Flow

### Invoice Processing Flow
1. **Upload**: File uploaded via `/api/v1/upload`
2. **Storage**: File saved to `uploads/` directory
3. **Database**: Invoice record created with "initiated" status
4. **Background Processing**: `process_invoice()` function called
5. **OCR Extraction**: PDF converted to images, OCR applied
6. **LLM Extraction**: Structured data extracted using LLM
7. **Comparison**: If reference data provided, LLM comparison performed
8. **Completion**: Status updated to "completed" or "failed"

### OCR Processing Flow
1. **Input**: Document (URL, base64, or file upload)
2. **Detection**: Document type auto-detected or specified
3. **Processing**: PDF converted to images if needed
4. **OCR**: Text extracted using PaddleOCR or Tesseract
5. **LLM Analysis**: Structured data extracted using LLM
6. **Response**: Cleaned JSON response returned

## Key Features

### Multi-Format Support
- **PDF**: Both text-based and scanned PDFs
- **Images**: JPEG, PNG formats
- **Base64**: Direct base64 encoded data
- **URLs**: Public URLs for document access

### Error Handling
- Comprehensive exception handling
- Graceful degradation
- Detailed error messages
- Background task cleanup

### Performance Optimizations
- Async processing for heavy operations
- Background task processing
- Connection pooling
- File cleanup automation

### Security Features
- JWT authentication
- File type validation
- File size limits
- CORS configuration
- Input sanitization

## Configuration Requirements

### Environment Variables
- `MYSQL_SERVER`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
- `SECRET_KEY` for JWT
- `GITHUB_INFERENCE_API_KEY` for LLM
- `OCR_LLM_BACKEND` (auto/github/ollama)

### Dependencies
- FastAPI, Uvicorn
- SQLAlchemy, MySQL client
- PaddleOCR, Tesseract, pdf2image
- Docling, pdfplumber
- OpenCV, Pillow
- Requests, Pydantic

## Development Notes

### Code Quality
- Type hints throughout
- Comprehensive error handling
- Modular design
- Clear separation of concerns

### Scalability Considerations
- Background task processing
- Database connection pooling
- Async operations
- File cleanup automation

### Future Enhancements
- Batch processing
- Webhook support
- Advanced analytics
- Custom field extraction
- API rate limiting
