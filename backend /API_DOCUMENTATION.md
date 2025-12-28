# Neura API - Complete API Documentation

## Overview

The Neura API is a comprehensive document processing service that provides OCR extraction, invoice processing, and document classification capabilities. The API supports multiple document types and formats with intelligent data extraction using LLM technology.

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**Content-Type**: `application/json` (except file uploads)

## Authentication

The API uses JWT-based authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Invoice Processing

#### Upload Invoice
**Endpoint**: `POST /api/v1/upload`  
**Description**: Upload an invoice file with optional reference data for processing

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (required): Invoice file (PDF, JPEG, PNG)
  - `reference_data` (optional): JSON file with reference data

**Response**:
```json
{
  "id": 123,
  "status": "initiated",
  "message": "File uploaded successfully"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid file type
- `500`: Server error

#### Get Processing Results
**Endpoint**: `GET /api/v1/results/{document_id}`  
**Description**: Retrieve processing results for a specific invoice

**Parameters**:
- `document_id` (path): Invoice ID

**Response**:
```json
{
  "id": 123,
  "name": "invoice.pdf",
  "created_by": "anonymous",
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:35:00Z",
  "status": "completed",
  "num_pages": 2,
  "pages": [
    {
      "number": 1,
      "page_type": "invoice",
      "key_values": {
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15",
        "vendor_name": "ABC Corp",
        "total_amount": 1000.00
      },
      "items": [
        [
          {
            "key": "description",
            "value": "Service Fee"
          },
          {
            "key": "amount",
            "value": 1000.00
          }
        ]
      ]
    }
  ],
  "extracted_data": {
    "invoice_metadata": {
      "document_no": "INV-001",
      "document_date": "2024-01-15"
    },
    "supplier": {
      "name": "ABC Corp",
      "gstin": "12ABCDE1234F1Z5"
    },
    "totals": {
      "total_invoice_amount": "1000.00"
    }
  },
  "reference_data": {
    "invoice_metadata": {
      "document_no": "INV-001",
      "document_date": "2024-01-15"
    }
  },
  "comparison": {
    "invoice_details": {
      "invoice_number": {
        "label": "Invoice Number",
        "value": "INV-001"
      }
    },
    "comparison_results": [
      {
        "field": "invoice_number",
        "label": "Invoice Number",
        "extracted_value": "INV-001",
        "expected_value": "INV-001",
        "match": true,
        "llm_analysis": "Values match perfectly"
      }
    ]
  },
  "reviewed": false,
  "error_message": null
}
```

#### List Documents
**Endpoint**: `GET /api/v1/documents`  
**Description**: List all processed documents with optional filtering

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `status` (optional): Filter by status (initiated, parsed, completed, failed)
- `date_from` (optional): Filter by start date (ISO format)
- `date_to` (optional): Filter by end date (ISO format)

**Response**:
```json
{
  "total": 50,
  "page": 1,
  "limit": 10,
  "documents": [
    {
      "id": 123,
      "name": "invoice.pdf",
      "created_by": "anonymous",
      "created_at": "2024-01-15T10:30:00Z",
      "processed_at": "2024-01-15T10:35:00Z",
      "status": "completed",
      "num_pages": 2,
      "extracted_data": {...},
      "reference_data": {...},
      "comparison": {...},
      "reviewed": false
    }
  ]
}
```

### 2. OCR Extraction

All OCR endpoints follow the same pattern with different document types.

#### PAN Card Extraction
**Endpoint**: `POST /api/v1/ocr/extract/pan`  
**Description**: Extract data from Indian PAN card

**Request**:
```json
{
  "documents": [
    "https://example.com/pan.jpg",
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "base64_encoded_string"
  ]
}
```

**Response**:
```json
{
  "results": {
    "name": "John Doe",
    "age": 30,
    "date_of_birth": "15/01/1994",
    "date_of_issue": "15/01/2020",
    "fathers_name": "Robert Doe",
    "pan_no": "ABCDE1234F",
    "aa": "1234567",
    "type": "ind_pan"
  }
}
```

#### Aadhaar Card Extraction
**Endpoint**: `POST /api/v1/ocr/extract/ind_aadhaar`  
**Description**: Extract data from Indian Aadhaar card

**Response**:
```json
{
  "results": {
    "full_address": "123 Main Street, City, State",
    "date_of_birth": "15/01/1994",
    "district": "Sample District",
    "fathers_name": "Robert Doe",
    "mobile": "9876543210",
    "gender": "Male",
    "house_no": "123",
    "aadhar_no": "1234 5678 9012",
    "name": "John Doe",
    "pincode": "123456",
    "state": "Sample State",
    "address_line": "Main Street",
    "type": "ind_aadhar"
  }
}
```

#### GST Certificate Extraction
**Endpoint**: `POST /api/v1/ocr/extract/gst`  
**Description**: Extract data from GST certificate

**Response**:
```json
{
  "results": {
    "address": "123 Business Street, City, State",
    "entity_type": "Private Limited Company",
    "incorporation_date": "15/01/2020",
    "gst_no": "12ABCDE1234F1Z5",
    "is_active": true,
    "legal_name": "ABC Private Limited",
    "pan_number": "ABCDE1234F",
    "trade_name": "ABC Corp",
    "type_of_registration": "Regular",
    "valid_from": "15/01/2020",
    "valid_upto": "14/01/2025",
    "type": "ind_gst_certificate"
  }
}
```

#### Cancelled Cheque Extraction
**Endpoint**: `POST /api/v1/ocr/extract/cheque`  
**Description**: Extract data from cancelled cheque

**Response**:
```json
{
  "results": {
    "account_holder_name": "John Doe",
    "account_no": "1234567890",
    "account_type": "Savings",
    "bank_address": "123 Bank Street, City",
    "bank_name": "Sample Bank",
    "date_of_issue": "15/01/2024",
    "ifsc_code": "HDFC0001234",
    "micr_cheque_no": "123456789",
    "micr_code": "123456789",
    "type": "ind_cheque"
  }
}
```

#### Voter ID Extraction
**Endpoint**: `POST /api/v1/ocr/extract/voterid`  
**Description**: Extract data from Indian Voter ID

**Response**:
```json
{
  "results": {
    "full_address": "123 Main Street, City, State",
    "age": "30",
    "date_of_birth": "15/01/1994",
    "district": "Sample District",
    "fathers_name": "Robert Doe",
    "gender": "Male",
    "house_number": "123",
    "voter_id": "ABC1234567",
    "name": "John Doe",
    "pincode": "123456",
    "state": "Sample State",
    "address_line": "Main Street",
    "year_of_birth": "1994",
    "type": "ind_voterid"
  }
}
```

#### Electricity Bill Extraction
**Endpoint**: `POST /api/v1/ocr/extract/ebbill`  
**Description**: Extract data from electricity bill

**Response**:
```json
{
  "results": {
    "consumer_name": "John Doe",
    "consumer_number": "1234567890",
    "service_number": "SVC123456",
    "bill_number": "EB123456",
    "bill_date": "15/01/2024",
    "due_date": "25/01/2024",
    "amount_due": "1500.75",
    "address": "123 Main Street, City, State",
    "city": "Sample City",
    "district": "Sample District",
    "state": "Sample State",
    "pincode": "123456",
    "month": "January 2024",
    "eb_provider": "Sample Power Company",
    "type": "ind_electricity_bill"
  }
}
```

#### Driving License Extraction
**Endpoint**: `POST /api/v1/ocr/extract/driving_license`  
**Description**: Extract data from Indian driving license

**Response**:
```json
{
  "results": {
    "full_address": "123 Main Street, City, State",
    "date_of_birth": "15/01/1994",
    "date_of_validity": "14/01/2029",
    "district": "Sample District",
    "fathers_name": "Robert Doe",
    "driving_license_no": "DL-0420110149646",
    "issue_dates": {
      "LMV": "15/01/2020",
      "MCWG": "15/01/2020",
      "TRANS": ""
    },
    "name": "John Doe",
    "pincode": "123456",
    "state": "Sample State",
    "address_line": "Main Street",
    "type": ["MCWG", "LMV"],
    "validity": {
      "NT": "14/01/2029",
      "T": "14/01/2029"
    },
    "type": "ind_driving_license"
  }
}
```

#### Udyog Aadhaar Extraction
**Endpoint**: `POST /api/v1/ocr/extract/udyog_aadhaar`  
**Description**: Extract data from Udyog Aadhaar certificate

**Response**:
```json
{
  "results": {
    "udyog_no": "123456789012",
    "address": "123 Business Street, City, State",
    "mobile": "9876543210",
    "incorporation_date": "2024-01-15",
    "district": "Sample District",
    "email": "john@example.com",
    "entity_type": "Private Limited Company",
    "industry_type": "Technology",
    "name": "ABC Private Limited",
    "pincode": "123456",
    "state": "Sample State",
    "type": "ind_udyog_aadhaar"
  }
}
```

#### Penny Drop Validation Extraction
**Endpoint**: `POST /api/v1/ocr/extract/penny_drop`  
**Description**: Extract data from penny drop validation document

**Response**:
```json
{
  "results": {
    "account_exists": "true",
    "amount_deposited": "1.00",
    "bank_account_number": "1234567890",
    "ifsc_code": "HDFC0001234",
    "name_at_bank": "John Doe",
    "micr_code": "123456789",
    "type": "validate_bank_account"
  }
}
```

#### Document Classification
**Endpoint**: `POST /api/v1/ocr/extract/classify`  
**Description**: Classify document type

**Response**:
```json
{
  "results": [
    {
      "type": "ind_pan"
    }
  ]
}
```

#### Water Bill Extraction
**Endpoint**: `POST /api/v1/ocr/extract/waterbill`  
**Description**: Extract data from water bill

**Response**:
```json
{
  "results": {
    "consumer_name": "John Doe",
    "consumer_number": "1234567890",
    "bill_number": "WB123456",
    "bill_date": "15/01/2024",
    "due_date": "25/01/2024",
    "amount_due": "500.25",
    "address": "123 Main Street, City, State",
    "city": "Sample City",
    "district": "Sample District",
    "state": "Sample State",
    "pincode": "123456",
    "month": "January 2024",
    "water_provider": "Sample Water Company",
    "type": "water_bill"
  }
}
```

#### Business Card Extraction
**Endpoint**: `POST /api/v1/ocr/extract/business_card`  
**Description**: Extract data from business card

**Response**:
```json
{
  "results": {
    "company_name": "ABC Corporation",
    "person_name": "John Doe",
    "designation": "Sales Manager",
    "email": "john.doe@abccorp.com",
    "phone": "+91-9876543210",
    "mobile": "9876543210",
    "address": "123 Business Street, City, State",
    "website": "www.abccorp.com",
    "fax": "+91-11-12345678",
    "type": "business_card"
  }
}
```

#### Name Board Extraction
**Endpoint**: `POST /api/v1/ocr/extract/name_board`  
**Description**: Extract data from name board/signboard

**Response**:
```json
{
  "results": {
    "business_name": "ABC Electronics",
    "business_type": "Electronics Store",
    "address": "123 Main Street, City, State",
    "phone": "9876543210",
    "email": "info@abcelectronics.com",
    "website": "www.abcelectronics.com",
    "established_year": "2010",
    "services": "Electronics, Mobile Phones, Laptops",
    "type": "name_board"
  }
}
```

#### Rental Agreement Extraction
**Endpoint**: `POST /api/v1/ocr/extract/rental_agreement`  
**Description**: Extract data from rental agreement

**Response**:
```json
{
  "results": {
    "landlord_name": "John Smith",
    "tenant_name": "Jane Doe",
    "property_address": "123 Main Street, City, State",
    "rent_amount": "25000",
    "security_deposit": "50000",
    "agreement_start_date": "01/01/2024",
    "agreement_end_date": "31/12/2024",
    "property_type": "2 BHK Apartment",
    "area_sqft": "1200",
    "landlord_pan": "ABCDE1234F",
    "tenant_pan": "FGHIJ5678K",
    "landlord_aadhaar": "1234 5678 9012",
    "tenant_aadhaar": "9876 5432 1098",
    "type": "rental_agreement"
  }
}
```

#### Property Tax Extraction
**Endpoint**: `POST /api/v1/ocr/extract/property_tax`  
**Description**: Extract data from property tax document

**Response**:
```json
{
  "results": {
    "property_owner_name": "John Doe",
    "property_address": "123 Main Street, City, State",
    "property_id": "PROP123456",
    "assessment_year": "2024-25",
    "tax_amount": "15000",
    "due_date": "31/03/2024",
    "payment_status": "Paid",
    "property_type": "Residential",
    "area_sqft": "1200",
    "municipality": "Sample Municipality",
    "ward_number": "Ward 5",
    "type": "property_tax"
  }
}
```

#### Shop License Extraction
**Endpoint**: `POST /api/v1/ocr/extract/shop_license`  
**Description**: Extract data from shop license certificate (handles multilingual and handwritten content)

**Response**:
```json
{
  "results": {
    "business_name": "ABC General Store",
    "license_number": "SL123456789",
    "license_type": "General Trade License",
    "owner_name": "John Doe",
    "business_address": "123 Main Street, City, State",
    "issue_date": "01/01/2024",
    "expiry_date": "31/12/2024",
    "business_category": "Retail Trade",
    "authority_issued": "Municipal Corporation",
    "validity_period": "1 Year",
    "type": "shop_license"
  }
}
```

#### Financial Statement Extraction
**Endpoint**: `POST /api/v1/ocr/extract/financial_statement`  
**Description**: Extract data from financial statement (attached to ITR-5)

**Response**:
```json
{
  "results": {
    "company_name": "ABC Private Limited",
    "financial_year": "2023-24",
    "total_revenue": "10000000",
    "total_expenses": "7500000",
    "net_profit": "2500000",
    "total_assets": "50000000",
    "total_liabilities": "20000000",
    "equity": "30000000",
    "cash_flow": "5000000",
    "auditor_name": "XYZ & Associates",
    "audit_date": "31/03/2024",
    "type": "financial_statement"
  }
}
```

#### Form 16 Extraction
**Endpoint**: `POST /api/v1/ocr/extract/form16`  
**Description**: Extract data from Form 16 document (both Part A and Part B) with all sensitive information including quarterly summaries, book adjustment deposits, and certificate details

**Response**:
```json
{
  "results": {
    "source_file": "AFXPB6378N_2023-24.pdf",
    "employer": {
      "name": "INFORVIO TECHNOLOGIES PRIVATE LIMITED",
      "address": "2, N G G O Colony, III Street,, Surampatti, Erode - 638009, Tamil Nadu",
      "phone": "+(91)4285-225893",
      "email": "incometaxgobi@rrpm.co.in",
      "pan": "AADCI4443H",
      "tan": "CMBI04126D"
    },
    "employee": {
      "name": "DEEPALI SRINIVAS",
      "address": "F 1 ANAND RESIDENCY, CHURCH STREET, OLD AIRPORT ROAD, MURUGESHPALYA, NEAR KEMPFORT MALL BANGAL - 560017 Karnataka",
      "pan": "AFXPB6378N"
    },
    "assessment_year": "2023-24",
    "cit_tds_office": {
      "name": "The Commissioner of Income Tax (TDS)",
      "address": "7th Floor, New Block, Aayakar Bhawan, 121 , M.G. Road, Chennai - 600034"
    },
    "employment_period": {
      "from": "01-Apr-2022",
      "to": "31-Mar-2023"
    },
    "quarterly_summary": [
      {
        "quarter": "Q1",
        "receipt_number_of_quarterly_statement": "FXBYFCCK",
        "amount_paid_credited": 154000.00,
        "tax_deducted": 9000.00,
        "tax_deposited": 9000.00
      },
      {
        "quarter": "Q2",
        "receipt_number_of_quarterly_statement": "FXBAEZLY",
        "amount_paid_credited": 165000.00,
        "tax_deducted": 9000.00,
        "tax_deposited": 9000.00
      },
      {
        "quarter": "Q3",
        "receipt_number_of_quarterly_statement": "FXBCGOBW",
        "amount_paid_credited": 176000.00,
        "tax_deducted": 9000.00,
        "tax_deposited": 9000.00
      },
      {
        "quarter": "Q4",
        "receipt_number_of_quarterly_statement": "FXBFMBUE",
        "amount_paid_credited": 198000.00,
        "tax_deducted": 9000.00,
        "tax_deposited": 9000.00
      }
    ],
    "totals": {
      "total_amount_paid_credited": 693000.00,
      "total_tax_deducted": 36000.00,
      "total_tax_deposited": 36000.00
    },
    "book_adjustment_deposits": [
      {
        "sl_no": 1,
        "tax_deposited": 3000.00,
        "book_identification_number": "0510308",
        "date_of_transfer_voucher": "27-05-2022",
        "challan_serial_number": "16243",
        "status_of_matching_with_24G": "F"
      }
    ],
    "certificate": {
      "certificate_no": "SOZVMCA",
      "last_updated_on": "23-Jul-2023",
      "declarant_name": "SREEDHAR RAMASAMY",
      "declarant_designation": "MANAGING DIRECTOR",
      "declarant_father_name": "RAMASAMY MUTHUSAMY",
      "verification_place": "ERODE",
      "verification_date": "28-Jul-2023"
    },
    "notes": [
      "Part B (Annexure) of the certificate in Form No.16 shall be issued by the employer.",
      "To update PAN details in Income Tax Department database, apply for 'PAN change request' through NSDL or UTITSL."
    ],
    "type": "form16"
  }
}
```

#### GST Return Extraction
**Endpoint**: `POST /api/v1/ocr/extract/gst_return`  
**Description**: Extract data from GST Return documents (GSTR-1, GSTR-3B, or other GST forms) with all sensitive information including taxpayer details, outward supplies, ITC details, and tax calculations

**Response**:
```json
{
  "results": {
    "taxpayer_info": {
      "gstin": "33AADCI4443H1ZT",
      "legal_name": "INFORVIO TECHNOLOGIES PRIVATE LIMITED",
      "trade_name": "INFORVIO TECHNOLOGIES PRIVATE LIMITED",
      "financial_year": "2025-26",
      "tax_period": "August",
      "filing_details": {
        "gstr1_filing_date": "2025-09-08",
        "gstr1a_filing_date": null,
        "gstr2b_generation_date": "2025-09-16",
        "gstr3b_generation_date": "2025-09-16"
      }
    },
    "outward_supplies": {
      "taxable_supplies_other_than_zero_rated": {
        "taxable_value": 949638.00,
        "integrated_tax": 170934.84,
        "central_tax": 0.00,
        "state_ut_tax": 0.00,
        "cess": 0.00
      },
      "taxable_supplies_zero_rated": {
        "taxable_value": 0.00,
        "integrated_tax": 0.00,
        "central_tax": 0.00,
        "state_ut_tax": 0.00,
        "cess": 0.00
      },
      "other_outward_supplies_nil_exempted": {
        "taxable_value": 0.00
      },
      "inward_supplies_reverse_charge": {
        "taxable_value": 0.00,
        "integrated_tax": 0.00,
        "central_tax": 0.00,
        "state_ut_tax": 0.00,
        "cess": 0.00
      },
      "non_gst_outward_supplies": {
        "taxable_value": 0.00
      }
    },
    "supplies_under_section_9_5": {
      "operator_pays_tax": {
        "taxable_value": 0.00,
        "integrated_tax": 0.00,
        "central_tax": 0.00,
        "state_ut_tax": 0.00,
        "cess": 0.00
      },
      "registered_person_supplies": {
        "taxable_value": 0.00,
        "integrated_tax": 0.00,
        "central_tax": 0.00,
        "state_ut_tax": 0.00,
        "cess": 0.00
      }
    },
    "inter_state_supplies_breakup": {
      "to_unregistered_persons": {
        "taxable_value": 0.00,
        "integrated_tax": 0.00
      },
      "to_composition_taxable_persons": {
        "taxable_value": 0.00,
        "integrated_tax": 0.00
      },
      "to_uin_holders": {
        "taxable_value": 0.00,
        "integrated_tax": 0.00
      }
    },
    "input_tax_credit": {
      "itc_available": {
        "import_of_goods": 0.00,
        "import_of_services": 0.00,
        "inward_supplies_reverse_charge": {
          "integrated_tax": 0.00,
          "central_tax": 0.00,
          "state_ut_tax": 0.00,
          "cess": 0.00
        },
        "inward_supplies_from_isd": {
          "integrated_tax": 0.00,
          "central_tax": 0.00,
          "state_ut_tax": 0.00,
          "cess": 0.00
        },
        "all_other_itc": {
          "integrated_tax": 55502.57,
          "central_tax": 432.99,
          "state_ut_tax": 432.99,
          "cess": 0.00
        }
      },
      "itc_reversed": {
        "as_per_rules": "Not Generated",
        "others": "Not Generated"
      },
      "net_itc_available": {
        "integrated_tax": 55502.57,
        "central_tax": 432.99,
        "state_ut_tax": 432.99,
        "cess": 0.00
      },
      "ineligible_itc": {
        "under_section_16_4": 0.00,
        "due_to_pos_rules": 0.00
      }
    },
    "interest_details": {
      "integrated_tax": "Not Available",
      "central_tax": "Not Available",
      "state_ut_tax": "Not Available",
      "cess": "Not Available"
    },
    "type": "gst_return"
  }
}
```

#### ITR Extraction
**Endpoint**: `POST /api/v1/ocr/extract/itr`  
**Description**: Extract data from Income Tax Return (ITR) documents with all sensitive information including acknowledgement details, taxpayer info, income tax calculations, verification details, and submission information

**Response**:
```json
{
  "results": {
    "itr_acknowledgement": {
      "acknowledgement_number": "203764081120121",
      "assessment_year": "2020-21",
      "form_number": "ITR-6",
      "filed_under_section": "139(1) - On or before due date",
      "status": "Pvt Company"
    },
    "taxpayer_info": {
      "pan": "AADCI4443H",
      "name": "INFORVIO TECHNOLOGIES PRIVATE LIMITED",
      "address": {
        "line1": "No.2, N G G O Colony IIIrd Street, Surampatti",
        "city": "Erode",
        "district": "Erode",
        "state": "Tamil Nadu",
        "pincode": "638009"
      }
    },
    "income_tax_details": {
      "book_profit_under_mat": 2050781.00,
      "current_year_business_loss": 0.00,
      "net_tax_payable": 0.00,
      "interest_and_fee_payable": 0.00,
      "total_tax_interest_fee_payable": 0.00,
      "taxes_paid": 865370.00,
      "tax_refund_or_payable": -865370.00,
      "total_income": 865368.00,
      "adjusted_total_income_under_amt": 0.00
    },
    "dividend_distribution_tax": {
      "dividend_tax_payable": 0.00,
      "interest_payable": 0.00,
      "total_dividend_tax_interest_payable": 0.00,
      "taxes_paid": 0.00,
      "tax_refund_or_payable": 0.00
    },
    "accreted_income_and_tax": {
      "accreted_income_115TD": 0.00,
      "additional_tax_payable_115TD": 0.00,
      "interest_payable_115TE": 0.00,
      "total_additional_tax_interest_payable": 0.00,
      "tax_and_interest_paid": 0.00,
      "tax_refund_or_payable": 0.00
    },
    "verification_details": {
      "verified_by": "SREEDHAR R",
      "verification_method": "Digital Signature Certificate (DSC)",
      "dsc_details": "CN=e-Mudhra Sub CA for Class 2 Individual 2014, OU=Certifying Authority, O=eMudhra Consumer Services Limited, C=IN",
      "ip_address": "103.148.33.236",
      "verification_date": "2021-01-12T18:51:14",
      "dsc_id": "AZEPR3130M"
    },
    "submission_details": {
      "submitted_from_ip": "103.148.33.236",
      "submission_date": "2021-01-12T18:51:14",
      "submitted_electronically": true
    },
    "sensitive_data_classification": {
      "identifiers": [
        "PAN",
        "IP Address",
        "Acknowledgement Number",
        "DSC ID"
      ],
      "financial_data": [
        "total_income",
        "book_profit_under_mat",
        "net_tax_payable",
        "taxes_paid"
      ],
      "personal_data": [
        "name",
        "address",
        "verified_by"
      ]
    },
    "type": "itr"
  }
}
```

#### Multi-Document Detection and Extraction
**Endpoint**: `POST /api/v1/ocr/extract/multi_document`  
**Description**: Detect and extract data from multiple document types in a single PDF. Automatically identifies and extracts data from all document types found including PAN, Aadhaar, Voter ID, Driving License, Cheque, GST Certificate, Udyog Aadhaar, Electricity Bill, Water Bill, Business Card, Name Board, Rental Agreement, Property Tax, Shop License, Financial Statement, Payslip, Form 16, GST Return, ITR, and other document types.

**Response**:
```json
{
  "results": {
    "detected_documents": [
      {
        "document_type": "ind_pan",
        "confidence": 0.95,
        "page_number": 1,
        "extracted_data": {
          "pan_number": "ABCDE1234F",
          "name": "JOHN DOE",
          "father_name": "RICHARD DOE",
          "date_of_birth": "01-Jan-1990",
          "signature": "JOHN DOE"
        }
      },
      {
        "document_type": "ind_aadhaar",
        "confidence": 0.92,
        "page_number": 2,
        "extracted_data": {
          "aadhaar_number": "123456789012",
          "name": "JOHN DOE",
          "father_name": "RICHARD DOE",
          "date_of_birth": "01-Jan-1990",
          "gender": "Male",
          "address": "123 Main Street, City, State 12345",
          "pin_code": "12345",
          "state": "State",
          "district": "District",
          "sub_district": "Sub District",
          "village_town": "Village",
          "post_office": "Post Office",
          "house_number": "123",
          "street": "Main Street",
          "landmark": "Near Park",
          "locality": "Locality",
          "qr_data": "QR_CODE_DATA"
        }
      },
      {
        "document_type": "ind_driving_license",
        "confidence": 0.90,
        "page_number": 3,
        "extracted_data": {
          "license_number": "DL1234567890123",
          "name": "JOHN DOE",
          "father_name": "RICHARD DOE",
          "date_of_birth": "01-Jan-1990",
          "address": "123 Main Street, City, State 12345",
          "pin_code": "12345",
          "state": "State",
          "district": "District",
          "valid_from": "01-Jan-2020",
          "valid_to": "01-Jan-2030",
          "vehicle_classes": "MCWG, LMV",
          "blood_group": "O+",
          "photo": "PHOTO_DATA"
        }
      }
    ],
    "summary": {
      "total_documents_found": 3,
      "document_types": ["ind_pan", "ind_aadhaar", "ind_driving_license"],
      "total_pages_processed": 3,
      "extraction_confidence": 0.92
    },
    "type": "multi_document"
  }
}
```

#### Insurance Policy Extraction
**Endpoint**: `POST /api/v1/ocr/extract/insurance`  
**Description**: Extract structured data from Indian vehicle insurance policy documents. Supports multiple pages and consolidates fields across sections.

**Request**:
```json
{
  "documents": [
    "https://example.com/policy.pdf",
    "data:application/pdf;base64,JVBERi0xLjQK...",
    "base64_encoded_string"
  ]
}
```

**Response**:
```json
{
  "results": {
    "policy_number": "TN/2024/ABC12345",
    "policy_type": "Comprehensive",
    "policy_issue_date": "01-Apr-2024",
    "policy_period": {"start": "01-Apr-2024", "end": "31-Mar-2025"},
    "insured_details": {"name": "", "address": "", "state": "", "gst_status": ""},
    "vehicle_details": {
      "make": "",
      "model": "",
      "registration_number": "",
      "year_of_manufacture": 0,
      "engine_number": "",
      "chassis_number": "",
      "fuel_type": "",
      "color": "",
      "rto_location": "",
      "insured_declared_value": 0
    },
    "nominee_details": {"name": "", "age": 0, "relationship": ""},
    "financier_details": {"type": "", "name": "", "branch": ""},
    "payment_details": {"mode": "", "transaction_number": "", "bank_name": "", "amount_paid": 0},
    "premium_details": {"own_damage": 0, "liability": 0, "total_premium": 0, "tax": 0, "gross_premium_paid": 0},
    "insurer_details": {"company_name": "", "policy_issuing_office": "", "gstin": "", "broker": "", "broker_contact": "", "broker_email": ""},
    "type": "ind_vehicle_insurance"
  }
}
```

#### Vehicle RC Extraction
**Endpoint**: `POST /api/v1/ocr/extract/vehicle_rc`  
**Description**: Extract structured data from Indian Vehicle Registration Certificate (RC Card).

**Request**:
```json
{
  "documents": [
    "https://example.com/rc.jpg",
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "base64_encoded_string"
  ]
}
```

**Response**:
```json
{
  "results": {
    "registration_number": "TN33BW6766",
    "chassis_number": "",
    "engine_number": "",
    "owner_name": "",
    "father_or_spouse_name": "",
    "address": "",
    "fuel_type": "",
    "maker_name": "",
    "model_name": "",
    "color": "",
    "body_type": "",
    "month_year_of_manufacture": "",
    "cubic_capacity": 0,
    "seating_capacity": 0,
    "wheel_base_mm": 0,
    "laden_weight_kg": 0,
    "unladen_weight_kg": 0,
    "registration_date": "",
    "registration_valid_till": "",
    "financier_name": "",
    "issuing_authority": "",
    "rto_location": "",
    "tax_paid_upto": "",
    "type": "ind_vehicle_rc"
  }
}
```

### 3. Bank Statement Processing

#### Process Bank Statement
**Endpoint**: `POST /api/v1/bank-statement/process`  
**Description**: Process bank statement PDF and extract transaction data

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (required): Bank statement PDF file

**Response**:
```json
{
  "statement_data": {
    "transactions": [
      {
        "date": "2024-01-15",
        "particulars": "Salary Credit",
        "transaction_type": "Credit",
        "amount": 50000.00,
        "type": "Credit",
        "balance": 50000.00
      },
      {
        "date": "2024-01-16",
        "particulars": "ATM Withdrawal",
        "transaction_type": "Debit",
        "amount": 2000.00,
        "type": "Debit",
        "balance": 48000.00
      }
    ],
    "total_transactions": 2,
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Bank Statement Health Check
**Endpoint**: `GET /api/v1/bank-statement/health`  
**Description**: Health check for bank statement processing service

**Response**:
```json
{
  "status": "healthy"
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid file type. Only PDF, JPEG, and PNG are supported."
}
```

#### 404 Not Found
```json
{
  "detail": "Invoice not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Processing failed: Error message here"
}
```

### Error Codes
- `400`: Bad Request - Invalid input or file type
- `401`: Unauthorized - Missing or invalid authentication
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server processing error

## Rate Limits

Currently, no rate limits are implemented. Consider implementing rate limiting for production use.

## File Upload Limits

- **Maximum file size**: 10MB
- **Supported formats**: PDF, JPEG, PNG
- **Processing timeout**: 60 seconds for OCR operations

## Data Formats

### Date Formats
- **API responses**: ISO 8601 format (`2024-01-15T10:30:00Z`)
- **OCR extraction**: DD/MM/YYYY format for Indian documents
- **Database storage**: UTC timestamps

### Currency Formats
- **API responses**: Decimal numbers (e.g., `1000.50`)
- **OCR extraction**: Plain numbers without currency symbols

### Document Types
All supported document types are prefixed with `ind_` for Indian documents:
- `ind_pan`, `comp_pan`
- `ind_aadhaar`
- `ind_voterid`
- `ind_driving_license`
- `ind_cheque`
- `ind_gst_certificate`
- `ind_udyog_aadhaar`
- `ind_electricity_bill`
- `water_bill`
- `validate_bank_account`
- `business_card`
- `name_board`
- `rental_agreement`
- `property_tax`
- `shop_license`
- `financial_statement`
- `form16`
- `gst_return`
- `itr`
- `multi_document`
- `payslip`
- `ind_vehicle_insurance`
- `ind_vehicle_rc`

## Examples

### Complete Invoice Processing Flow

1. **Upload Invoice**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Authorization: Bearer your_jwt_token" \
  -F "file=@invoice.pdf" \
  -F "reference_data=@reference.json"
```

2. **Check Processing Status**:
```bash
curl -X GET "http://localhost:8000/api/v1/results/123" \
  -H "Authorization: Bearer your_jwt_token"
```

3. **List All Documents**:
```bash
curl -X GET "http://localhost:8000/api/v1/documents?page=1&limit=10&status=completed" \
  -H "Authorization: Bearer your_jwt_token"
```

### OCR Extraction Example

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract/pan" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/pan.jpg",
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    ]
  }'
```

### Form 16 Extraction Example

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract/form16" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/form16.pdf",
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    ]
  }'
```

### GST Return Extraction Example

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract/gst_return" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/gstr3b.pdf",
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    ]
  }'
```

### ITR Extraction Example

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract/itr" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/itr_acknowledgement.pdf",
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    ]
  }'
```

### Multi-Document Detection Example

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract/multi_document" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/multiple_documents.pdf",
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    ]
  }'
```

### Insurance Policy Extraction Example

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract/insurance" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/vehicle_policy.pdf"
    ]
  }'
```

### Vehicle RC Extraction Example

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract/vehicle_rc" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/rc_card.jpg"
    ]
  }'
```

## SDK and Client Libraries

Currently, no official SDKs are provided. The API follows REST conventions and can be consumed using any HTTP client library.

## Support

For technical support or questions about the API, please refer to the project documentation or contact the development team.
