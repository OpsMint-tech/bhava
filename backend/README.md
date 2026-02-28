# Invoice Processing Service

A FastAPI-based service for processing invoices, extracting metadata, and comparing with reference data using LLM.

## Features

- Upload and process invoice files (PDF, JPEG, PNG)
- Extract metadata using OCR
- Compare extracted data with reference data using LLM
- RESTful API endpoints
- Authentication and authorization
- Background task processing
- MySQL database integration

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- Tesseract OCR
- Poppler (for PDF processing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd invoice-processing-service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up the database:
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE invoice_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Run migrations
alembic upgrade head
```

## Running the Service

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

### 1. Upload Invoice
- **POST** `/api/v1/upload`
- Upload an invoice file and optional reference data
- Requires authentication

### 2. Get Results
- **GET** `/api/v1/results/{document_id}`
- Get processing results for a specific invoice
- Requires authentication

### 3. List Documents
- **GET** `/api/v1/documents`
- List all processed documents with optional filtering
- Requires authentication

## Development

### Project Structure
```
app/
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base_class.py
│   └── session.py
├── models/
│   └── invoice.py
├── schemas/
│   └── invoice.py
├── services/
│   ├── invoice_processor.py
│   └── llm_service.py
└── main.py
```

### Adding New Features

1. Create new models in `app/models/`
2. Add schemas in `app/schemas/`
3. Implement services in `app/services/`
4. Add API endpoints in `app/main.py`

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 