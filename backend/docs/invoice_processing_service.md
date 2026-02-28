# Invoice Processing Service

## Overview
This service processes invoices, extracts metadata, and compares it with reference data using LLM for intelligent discrepancy detection.

## API Endpoints

### 1. Upload API
**Endpoint:** `/api/v1/upload`
**Method:** POST
**Content-Type:** multipart/form-data

**Request Body:**
- `file`: Invoice file (PDF/Image)
- `reference_data`: JSON file containing reference data (optional)

**Response:**
```json
{
    "id": "string",
    "status": "processing",
    "message": "File uploaded successfully"
}
```

### 2. Result API
**Endpoint:** `/api/v1/results/{document_id}`
**Method:** GET

**Response:**
```json
{
    "id": "string",
    "name": "string",
    "created_by": "string",
    "created_at": "datetime",
    "processed_at": "datetime",
    "status": "completed|processing|failed",
    "num_pages": "integer",
    "pages": [
        {
            "number": "integer",
            "page_type": "string",
            "key_values": {
                "invoice_number": "string",
                "invoice_date": "date",
                "po_number": "string",
                "vendor_name": "string",
                "vendor_gstin": "string",
                "vendor_address": "string",
                "lessor_name": "string",
                "lessor_gstin": "string",
                "lessor_address": "string",
                "lessee_name": "string",
                "lessee_gstin": "string",
                "lessee_address": "string",
                "total_cgst": "number",
                "total_sgst": "number",
                "total_igst": "number",
                "total_tcs": "number",
                "total_cess": "number",
                "total_amount": "number",
                "invoice_hsn": "string",
                "car_model": "string",
                "car_engine_number": "string",
                "car_chassis_number": "string",
                "SellerGstin": "string",
                "BuyerGstin": "string",
                "DocNo": "string",
                "DocTyp": "string",
                "DocDt": "date",
                "TotInvVal": "number",
                "ItemCnt": "string",
                "MainHsnCode": "string",
                "Irn": "string",
                "IrnDt": "date",
                "iss": "string",
                "qr_image": "string"
            },
            "items": [
                [
                    {
                        "key": "string",
                        "value": "string|number|null"
                    }
                ]
            ]
        }
    ],
    "reviewed": "boolean",
    "discrepancies": [
        {
            "field": "string",
            "extracted_value": "string|number|null",
            "reference_value": "string|number|null",
            "confidence": "number",
            "llm_analysis": "string"
        }
    ]
}
```

### 3. Document List API
**Endpoint:** `/api/v1/documents`
**Method:** GET

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `status`: Filter by status (optional)
- `date_from`: Filter by start date (optional)
- `date_to`: Filter by end date (optional)

**Response:**
```json
{
    "total": "integer",
    "page": "integer",
    "limit": "integer",
    "documents": [
        {
            "id": "string",
            "name": "string",
            "created_by": "string",
            "created_at": "datetime",
            "processed_at": "datetime",
            "status": "string",
            "num_pages": "integer",
            "reviewed": "boolean"
        }
    ]
}
```

## Technical Requirements

### 1. File Processing
- Support for PDF and image formats (PNG, JPG, JPEG)
- OCR processing for text extraction
- Multi-page document handling
- Metadata extraction using ML models

### 2. LLM Integration
- Use LLM for intelligent comparison between extracted and reference data
- Generate detailed discrepancy analysis
- Provide confidence scores for extracted data
- Context-aware field matching

### 3. Data Storage
- Store original documents
- Store extracted metadata
- Store processing results
- Store reference data

### 4. Security
- Authentication required for all endpoints
- File type validation
- File size limits
- Secure file storage

### 5. Error Handling
- Invalid file format handling
- Processing failure handling
- API error responses
- Validation errors

## Implementation Notes

1. Use async processing for file uploads
2. Implement webhook support for processing completion
3. Cache frequently accessed data
4. Implement rate limiting
5. Add logging for debugging and monitoring
6. Implement retry mechanism for failed processing
7. Add data validation before storage
8. Implement proper error handling and reporting

## Future Enhancements

1. Support for more file formats
2. Batch processing capability
3. Custom field extraction
4. Advanced analytics dashboard
5. Export functionality
6. API key management
7. Webhook customization
8. Custom validation rules

## LLM Integration (GitHub Inference API)

### Configuration
```python
GITHUB_INFERENCE_API_URL = "https://models.github.ai/inference/chat/completions"
GITHUB_INFERENCE_API_KEY = "your_api_key_here"
```

### API Usage
```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GITHUB_INFERENCE_API_KEY}"
}

payload = {
    "model": "openai/gpt-4.1",
    "temperature": 1,
    "top_p": 1,
    "messages": [
        {
            "role": "system",
            "content": "You are an expert in analyzing invoice data and identifying discrepancies between extracted and reference data."
        },
        {
            "role": "user",
            "content": "Compare the following extracted invoice data with reference data and identify any discrepancies..."
        }
    ]
}
```

### LLM Analysis Process
1. Extract metadata from invoice using OCR
2. Format extracted data and reference data for LLM analysis
3. Send to GitHub Inference API for intelligent comparison
4. Process LLM response to identify discrepancies
5. Store analysis results with confidence scores

### Example LLM Prompt
```json
{
    "role": "system",
    "content": "You are an expert in analyzing invoice data. Your task is to compare extracted invoice data with reference data and identify any discrepancies. Consider the following aspects:\n1. Field value matching\n2. Format consistency\n3. Business logic validation\n4. Context-aware comparison\nProvide detailed analysis with confidence scores."
}
```

### LLM Response Format
```json
{
    "discrepancies": [
        {
            "field": "invoice_number",
            "extracted_value": "INV-001",
            "reference_value": "INV-002",
            "confidence": 0.95,
            "llm_analysis": "The invoice numbers do not match. The extracted value 'INV-001' differs from the reference value 'INV-002'. This is a critical discrepancy that needs attention.",
            "severity": "high"
        }
    ],
    "summary": "Found 1 critical discrepancy in invoice number matching.",
    "confidence_score": 0.95
}
``` 