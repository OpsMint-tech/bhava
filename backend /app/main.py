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
from app.services.ocr_extractor import _extract_from_bytes, _clean_gpt_json, mask_pii

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
        
        # Parse JSON if it's a string, then always apply masking
        if isinstance(result, str):
            cleaned = _clean_gpt_json(result)
            data = mask_pii(json.loads(cleaned))
        elif isinstance(result, dict):
            data = mask_pii(result)
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
        
        # Parse JSON if it's a string, then always apply masking
        if isinstance(result, str):
            cleaned = _clean_gpt_json(result)
            data = mask_pii(json.loads(cleaned))
        elif isinstance(result, dict):
            data = mask_pii(result)
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
        
        # Parse JSON if it's a string, then always apply masking
        if isinstance(result, str):
            cleaned = _clean_gpt_json(result)
            data = mask_pii(json.loads(cleaned))
        elif isinstance(result, dict):
            data = mask_pii(result)
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

            # Merge results - _extract_from_bytes returns a dict/string/list
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

    # Final masking pass to ensure PAN/IFSC are always masked
    return {"results": mask_pii(merged_result)}


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

            # Merge results - _extract_from_bytes returns a dict/string/list
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

    # Final masking pass to ensure Aadhaar/account numbers are always masked
    return {"results": mask_pii(merged_result)}


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

            # Merge results - _extract_from_bytes returns a dict/string/list
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

    # Final masking pass to ensure voter_id is always masked
    return {"results": mask_pii(merged_result)}

@app.post("/api/v1/ocr/upload/cheque")
async def upload_cheque(file: UploadFile = File(...)):
    """
    Upload Bank Cheque image, save to uploads folder, and extract + mask data.
    PAN (if present) and IFSC will be masked before returning.
    """
    try:
        file_bytes = await file.read()

        file_extension = Path(file.filename).suffix or ".jpg"
        unique_filename = f"cheque_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        result = _extract_from_bytes(file_bytes, file.filename, "ind_cheque")

        if isinstance(result, str):
            cleaned = _clean_gpt_json(result)
            data = mask_pii(json.loads(cleaned))
        elif isinstance(result, dict):
            data = mask_pii(result)
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


@app.post("/api/v1/ocr/extract/cheque")
async def extract_cheque(payload: dict = Body(...)):
    """
    Extract bank cheque data from base64 or URL.
    PAN and IFSC will be masked before returning.
    """
    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        raise HTTPException(status_code=400, detail="documents must be a non-empty list")

    merged_result: Dict[str, Any] = {}

    for doc in documents:
        try:
            if doc.startswith("http://") or doc.startswith("https://"):
                resp = requests.get(doc, stream=True, timeout=60)
                resp.raise_for_status()
                filename = doc.split("/")[-1].split("?")[0]
                file_bytes = resp.content
                result = _extract_from_bytes(file_bytes, filename, "ind_cheque")
            else:
                b64_part = doc.split(",", 1)[1] if doc.startswith("data:") else doc
                file_bytes = base64.b64decode(b64_part)
                filename = "upload.jpg"
                result = _extract_from_bytes(file_bytes, filename, "ind_cheque")

            if isinstance(result, str):
                try:
                    cleaned = _clean_gpt_json(result)
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, dict):
                        merged_result.update(parsed)
                except json.JSONDecodeError as e:
                    merged_result["error"] = f"JSON parse error: {e}"
            elif isinstance(result, dict):
                merged_result.update(result)
            elif isinstance(result, list):
                for r in result:
                    if isinstance(r, dict):
                        merged_result.update(r)
                    elif isinstance(r, str):
                        try:
                            parsed = json.loads(_clean_gpt_json(r))
                            if isinstance(parsed, dict):
                                merged_result.update(parsed)
                        except Exception:
                            pass
        except Exception as e:
            merged_result["error"] = str(e)

    return {"results": mask_pii(merged_result)}


def _is_masked(value: str) -> bool:
    """Return True if a field value has been masked (i.e., contains 'X' characters)."""
    if not value:
        return False
    return "X" in str(value).upper()


@app.post("/api/v1/verify/bank-details")
async def verify_bank_details(payload: dict = Body(...)):
    """
    Section-4 verification endpoint.
    Accepts bank details data (with pan_no / ifsc fields) and checks
    whether both PAN and IFSC are properly masked.

    Returns:
        success=True  – both PAN and IFSC are masked
        success=False – one or both are NOT masked (raw values exposed)
    """
    data: Dict[str, Any] = payload.get("data", payload)

    # Support multiple PAN field names
    pan_value = (
        data.get("pan_no")
        or data.get("pan")
        or data.get("pan_number")
        or data.get("pan_card")
        or ""
    )

    # Support multiple IFSC field names
    ifsc_value = (
        data.get("ifsc")
        or data.get("ifsc_code")
        or data.get("bank_ifsc")
        or ""
    )

    pan_masked = _is_masked(str(pan_value)) if pan_value else True   # no PAN field = not applicable
    ifsc_masked = _is_masked(str(ifsc_value)) if ifsc_value else True # no IFSC field = not applicable

    failures = []
    if pan_value and not pan_masked:
        failures.append("PAN is not masked")
    if ifsc_value and not ifsc_masked:
        failures.append("IFSC is not masked")

    if failures:
        return {
            "success": False,
            "message": "Verification failed: " + ", ".join(failures),
            "pan_masked": pan_masked,
            "ifsc_masked": ifsc_masked,
        }

    return {
        "success": True,
        "message": "Verification passed: PAN and IFSC are properly masked",
        "pan_masked": pan_masked,
        "ifsc_masked": ifsc_masked,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
