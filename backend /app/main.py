from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import json
import base64
import requests
import os
import uuid
from pathlib import Path

# Import local modules
# We assume ocr_extractor is in app/services/ocr_extractor.py
from app.services.ocr_extractor import _extract_from_bytes, _clean_gpt_json

app = FastAPI(
    title="Neura API",
    description="Service for processing documents",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Neura API is running"}

# ========================================
# File Upload Endpoints
# ========================================
@app.post("/api/v1/ocr/upload/pan")
async def upload_pan(file: UploadFile = File(...)):
    """
    Upload PAN card image, save to uploads folder, and extract data.
    """
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix or ".jpg"
        unique_filename = f"pan_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        # Extract data
        result = _extract_from_bytes(file_bytes, file.filename, "ind_pan")
        
        # Parse JSON if it's a string
        if isinstance(result, str):
            cleaned = _clean_gpt_json(result)
            data = json.loads(cleaned)
        else:
            data = result
        
        return {
            "success": True,
            "file_path": str(file_path),
            "data": data
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/v1/ocr/upload/ind_aadhaar")
async def upload_aadhaar(file: UploadFile = File(...)):
    """
    Upload Aadhaar card image, save to uploads folder, and extract data.
    """
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix or ".jpg"
        unique_filename = f"aadhaar_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        # Extract data
        result = _extract_from_bytes(file_bytes, file.filename, "ind_aadhaar")
        
        # Parse JSON if it's a string
        if isinstance(result, str):
            cleaned = _clean_gpt_json(result)
            data = json.loads(cleaned)
        else:
            data = result
        
        return {
            "success": True,
            "file_path": str(file_path),
            "data": data
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/v1/ocr/upload/voterid")
async def upload_voterid(file: UploadFile = File(...)):
    """
    Upload Voter ID image, save to uploads folder, and extract data.
    """
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix or ".jpg"
        unique_filename = f"voterid_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        # Extract data
        result = _extract_from_bytes(file_bytes, file.filename, "ind_voterid")
        
        # Parse JSON if it's a string
        if isinstance(result, str):
            cleaned = _clean_gpt_json(result)
            data = json.loads(cleaned)
        else:
            data = result
        
        return {
            "success": True,
            "file_path": str(file_path),
            "data": data
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/v1/ocr/extract/pan")
async def extract_ind_pan(payload: dict = Body(...)):
    """
    Extract PAN data.
    """
    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        raise HTTPException(status_code=400, detail="documents must be a non-empty list")
    
    merged_result: Dict[str, Any] = {}

    for doc in documents:
        try:
            # --- URL ---
            if doc.startswith("http://") or doc.startswith("https://"):
                resp = requests.get(doc, stream=True, timeout=60)
                resp.raise_for_status()
                filename = doc.split("/")[-1].split("?")[0]
                file_bytes = resp.content
                detected_type = "ind_pan"
                result = _extract_from_bytes(file_bytes, filename, detected_type)

            # --- Base64 ---
            else:
                b64_part = doc.split(",", 1)[1] if doc.startswith("data:") else doc
                file_bytes = base64.b64decode(b64_part)
                filename = "upload.jpg"
                detected_type = "ind_pan"
                result = _extract_from_bytes(file_bytes, filename, detected_type)

            # Merge results - _extract_from_bytes returns a JSON string
            if isinstance(result, str):
                try:
                    cleaned = _clean_gpt_json(result)
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, dict):
                        merged_result.update(parsed)
                except json.JSONDecodeError as e:
                    merged_result["error"] = f"JSON parse error: {e}"
                    merged_result["raw"] = result
            elif isinstance(result, dict):
                merged_result.update(result)
            elif isinstance(result, list):
                 # Handle list return if any
                 for r in result:
                    if isinstance(r, dict):
                        merged_result.update(r)
                    elif isinstance(r, str):
                        try:
                            cleaned = _clean_gpt_json(r)
                            parsed = json.loads(cleaned)
                            if isinstance(parsed, dict):
                                merged_result.update(parsed)
                        except Exception:
                            pass

        except Exception as e:
            merged_result["error"] = str(e)

    return {"results": merged_result}


@app.post("/api/v1/ocr/extract/ind_aadhaar")
async def extract_ind_aadhaar(payload: dict = Body(...)):
    """
    Extract Aadhaar data.
    """
    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        raise HTTPException(status_code=400, detail="documents must be a non-empty list")
    
    merged_result: Dict[str, Any] = {}

    for doc in documents:
        try:
            # --- URL ---
            if doc.startswith("http://") or doc.startswith("https://"):
                resp = requests.get(doc, stream=True, timeout=60)
                resp.raise_for_status()
                filename = doc.split("/")[-1].split("?")[0]
                file_bytes = resp.content
                detected_type = "ind_aadhaar"
                result = _extract_from_bytes(file_bytes, filename, detected_type)

            # --- Base64 ---
            else:
                b64_part = doc.split(",", 1)[1] if doc.startswith("data:") else doc
                file_bytes = base64.b64decode(b64_part)
                filename = "upload.jpg"
                detected_type = "ind_aadhaar"
                result = _extract_from_bytes(file_bytes, filename, detected_type)

            # Merge results - _extract_from_bytes returns a JSON string
            if isinstance(result, str):
                try:
                    cleaned = _clean_gpt_json(result)
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, dict):
                        merged_result.update(parsed)
                except json.JSONDecodeError as e:
                    merged_result["error"] = f"JSON parse error: {e}"
                    merged_result["raw"] = result
            elif isinstance(result, dict):
                merged_result.update(result)
            elif isinstance(result, list):
                 for r in result:
                    if isinstance(r, dict):
                        merged_result.update(r)
                    elif isinstance(r, str):
                        try:
                            cleaned = _clean_gpt_json(r)
                            parsed = json.loads(cleaned)
                            if isinstance(parsed, dict):
                                merged_result.update(parsed)
                        except Exception:
                            pass

        except Exception as e:
            merged_result["error"] = str(e)

    return {"results": merged_result}


@app.post("/api/v1/ocr/extract/voterid")
async def extract_voter_id(payload: dict = Body(...)):
    """
    Extract Voter ID data.
    """
    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        raise HTTPException(status_code=400, detail="documents must be a non-empty list")

    merged_result: Dict[str, Any] = {}

    for doc in documents:
        try:
            # --- URL ---
            if doc.startswith("http://") or doc.startswith("https://"):
                resp = requests.get(doc, stream=True, timeout=60)
                resp.raise_for_status()
                filename = doc.split("/")[-1].split("?")[0]
                file_bytes = resp.content
                detected_type = "ind_voterid"
                result = _extract_from_bytes(file_bytes, filename, detected_type)

            # --- Base64 ---
            else:
                b64_part = doc.split(",", 1)[1] if doc.startswith("data:") else doc
                file_bytes = base64.b64decode(b64_part)
                filename = "upload.jpg"
                detected_type = "ind_voterid"
                result = _extract_from_bytes(file_bytes, filename, detected_type)

            # Merge results - _extract_from_bytes returns a JSON string
            if isinstance(result, str):
                try:
                    cleaned = _clean_gpt_json(result)
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, dict):
                        merged_result.update(parsed)
                except json.JSONDecodeError as e:
                    merged_result["error"] = f"JSON parse error: {e}"
                    merged_result["raw"] = result
            elif isinstance(result, dict):
                merged_result.update(result)
            elif isinstance(result, list):
                 for r in result:
                    if isinstance(r, dict):
                        merged_result.update(r)
                    elif isinstance(r, str):
                        try:
                            cleaned = _clean_gpt_json(r)
                            parsed = json.loads(cleaned)
                            if isinstance(parsed, dict):
                                merged_result.update(parsed)
                        except Exception:
                            pass

        except Exception as e:
            merged_result["error"] = str(e)

    return {"results": merged_result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
