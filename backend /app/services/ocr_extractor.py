import os
import base64
from io import BytesIO
from typing import List, Dict, Any
import requests
import re
import json
import pdfplumber
from pdf2image import convert_from_bytes
from dotenv import load_dotenv
from paddleocr import PaddleOCR
import cv2
import numpy as np

# Load environment variables once
load_dotenv()

_GITHUB_API_URL = "https://models.github.ai/inference/chat/completions"
_GITHUB_API_KEY = os.getenv("GITHUB_INFERENCE_API_KEY", "")
_DEFAULT_MODEL = os.getenv("GITHUB_INFERENCE_MODEL", "openai/gpt-4.1")

# Ollama-compatible settings (fallback)
_OLLAMA_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
_OLLAMA_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
_OLLAMA_MODEL = os.getenv("MODEL", "llama3.2-vision:latest")

# Backend selection: auto | github | ollama
_OCR_LLM_BACKEND = os.getenv("OCR_LLM_BACKEND", "auto").lower()

# ----------------------------
# Prompt templates
# ----------------------------
_PAN_PROMPT = (
    "Analyse the given Indian PAN card and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"name\": \"\",\n"
    "  \"age\": 0,\n"
    "  \"date_of_birth\": \"\",\n"
    "  \"date_of_issue\": \"\",\n"
    "  \"fathers_name\": \"\",\n"
    "  \"pan_no\": \"\",\n"
    "  \"aa\": \"\",\n"
    "  \"type\": \"ind_pan\"\n"
    "}\n"
    "Rules:\n"
    "- PAN number format is 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F).\n"
    "- Date of Birth must be DD/MM/YYYY.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_AADHAAR_PROMPT = (
    "Analyse the given Indian Aadhaar card and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"full_address\": \"\",\n"
    "  \"date_of_birth\": \"\",\n"
    "  \"district\": \"\",\n"
    "  \"fathers_name\": \"\",\n"
    "  \"mobile\": \"\",\n"
    "  \"gender\": \"\",\n"
    "  \"house_no\": \"\",\n"
    "  \"aadhar_no\": \"\",\n"
    "  \"name\": \"\",\n"
    "  \"pincode\": \"\",\n"
    "  \"state\": \"\",\n"
    "  \"address_line\": \"\",\n"
    "  \"type\": \"ind_aadhar\"\n"
    "}\n"
    "Rules:\n"
    "- Aadhaar number format is 12 digits (e.g., 1234 5678 9012).\n"
    "- Date of Birth must be DD/MM/YYYY.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_COMPANY_PAN_PROMPT = (
    "Analyse the given Indian Company PAN card and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"company_name\": \"\",\n"
    "  \"date_of_incorporation\": \"\",\n"
    "  \"pan_no\": \"\",\n"
    "  \"type\": \"comp_pan\"\n"
    "}\n"
    "Rules:\n"
    "- PAN number format is 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F).\n"
    "- Date must be DD/MM/YYYY.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_VOTER_ID_PROMPT = (
    "Analyse the given Indian Voter ID card and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"full_address\": \"\",\n"
    "  \"age\": \"\",\n"
    "  \"date_of_birth\": \"\",\n"
    "  \"district\": \"\",\n"
    "  \"fathers_name\": \"\",\n"
    "  \"gender\": \"\",\n"
    "  \"house_number\": \"\",\n"
    "  \"voter_id\": \"\",\n"
    "  \"name\": \"\",\n"
    "  \"pincode\": \"\",\n"
    "  \"state\": \"\",\n"
    "  \"address_line\": \"\",\n"
    "  \"year_of_birth\": \"\",\n"
    "  \"type\": \"ind_voterid\"\n"
    "}\n"
    "Rules:\n"
    "- Voter ID format: 3 letters + 7 digits (e.g., ABC1234567).\n"
    "- DOB or YOB must be DD/MM/YYYY or YYYY.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_GST_PROMPT = (
    "Analyse the given Indian GST Certificate and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"gstin\": \"\",\n"
    "  \"legal_name\": \"\",\n"
    "  \"trade_name\": \"\",\n"
    "  \"date_of_registration\": \"\",\n"
    "  \"state\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"type\": \"ind_gst_certificate\"\n"
    "}\n"
    "Rules:\n"
    "- GSTIN is 15 characters.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_CHEQUE_PROMPT = (
    "Analyse the given Indian Bank Cheque image and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"account_holder_name\": \"\",\n"
    "  \"bank_name\": \"\",\n"
    "  \"account_number\": \"\",\n"
    "  \"ifsc\": \"\",\n"
    "  \"micr_code\": \"\",\n"
    "  \"cheque_number\": \"\",\n"
    "  \"branch\": \"\",\n"
    "  \"type\": \"ind_cheque\"\n"
    "}\n"
    "Rules:\n"
    "- IFSC format is 11 characters (4 letters, 0, 6 alphanumeric).\n"
    "- Account number is numeric, typically 9-18 digits.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_PENNYDROP_PROMPT = (
    "Analyse the given bank account validation document or penny drop confirmation and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"account_holder_name\": \"\",\n"
    "  \"bank_name\": \"\",\n"
    "  \"account_number\": \"\",\n"
    "  \"ifsc\": \"\",\n"
    "  \"branch\": \"\",\n"
    "  \"account_type\": \"\",\n"
    "  \"verification_status\": \"\",\n"
    "  \"type\": \"validate_bank_account\"\n"
    "}\n"
    "Rules:\n"
    "- IFSC format is 11 characters.\n"
    "- Account number is numeric.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_DRIVING_LICENSE_PROMPT = (
    "Analyse the given Indian Driving License and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"name\": \"\",\n"
    "  \"date_of_birth\": \"\",\n"
    "  \"dl_number\": \"\",\n"
    "  \"issue_date\": \"\",\n"
    "  \"valid_till\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"vehicle_class\": \"\",\n"
    "  \"issuing_authority\": \"\",\n"
    "  \"type\": \"ind_driving_license\"\n"
    "}\n"
    "Rules:\n"
    "- DL number format varies by state.\n"
    "- Dates must be DD/MM/YYYY.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_UDYOG_AADHAAR_PROMPT = (
    "Analyse the given Indian Udyog Aadhaar (MSME) certificate and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"enterprise_name\": \"\",\n"
    "  \"udyog_aadhaar_number\": \"\",\n"
    "  \"owner_name\": \"\",\n"
    "  \"category\": \"\",\n"
    "  \"nic_code\": \"\",\n"
    "  \"state\": \"\",\n"
    "  \"district\": \"\",\n"
    "  \"date_of_commencement\": \"\",\n"
    "  \"type\": \"ind_udyog_aadhaar\"\n"
    "}\n"
    "Rules:\n"
    "- Udyog Aadhaar number is 12 digits.\n"
    "- Return ONLY the JSON, no extra text.\n"
)

_CLASSIFY_PROMPT = (
    "Look at the given document image and classify it. Return ONLY a JSON object like:\n"
    "{\"doc_type\": \"ind_pan\"}\n"
    "Possible doc_type values: ind_pan, comp_pan, ind_aadhar, ind_voterid, ind_driving_license, ind_gst_certificate, ind_cheque, ind_udyog_aadhaar, ind_electricity_bill, water_bill, payslip, business_card, name_board, rental_agreement, property_tax, shop_license, financial_statement, form16, gst_return, itr, insurance_document, vehicle_rc, unknown.\n"
    "Return ONLY the JSON, no extra text.\n"
)

_EB_BILL_PROMPT = (
    "Analyse the given Indian Electricity Bill and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"consumer_name\": \"\",\n"
    "  \"consumer_number\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"bill_date\": \"\",\n"
    "  \"due_date\": \"\",\n"
    "  \"units_consumed\": \"\",\n"
    "  \"amount_due\": \"\",\n"
    "  \"service_provider\": \"\",\n"
    "  \"type\": \"ind_electricity_bill\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_WATER_BILL_PROMPT = (
    "Analyse the given Water Bill and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"consumer_name\": \"\",\n"
    "  \"consumer_number\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"bill_date\": \"\",\n"
    "  \"due_date\": \"\",\n"
    "  \"amount_due\": \"\",\n"
    "  \"service_provider\": \"\",\n"
    "  \"type\": \"water_bill\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_PAYS_LIP_PROMPT = (
    "Analyse the given Payslip and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"employee_name\": \"\",\n"
    "  \"employee_id\": \"\",\n"
    "  \"designation\": \"\",\n"
    "  \"department\": \"\",\n"
    "  \"pay_period\": \"\",\n"
    "  \"gross_salary\": \"\",\n"
    "  \"net_salary\": \"\",\n"
    "  \"deductions\": \"\",\n"
    "  \"employer_name\": \"\",\n"
    "  \"type\": \"payslip\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_BUSINESS_CARD_PROMPT = (
    "Analyse the given Business Card and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"name\": \"\",\n"
    "  \"designation\": \"\",\n"
    "  \"company_name\": \"\",\n"
    "  \"phone\": \"\",\n"
    "  \"email\": \"\",\n"
    "  \"website\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"type\": \"business_card\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_NAME_BOARD_PROMPT = (
    "Analyse the given Name Board image and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"business_name\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"phone\": \"\",\n"
    "  \"type\": \"name_board\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_RENTAL_AGREEMENT_PROMPT = (
    "Analyse the given Rental Agreement document and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"landlord_name\": \"\",\n"
    "  \"tenant_name\": \"\",\n"
    "  \"property_address\": \"\",\n"
    "  \"monthly_rent\": \"\",\n"
    "  \"lease_start_date\": \"\",\n"
    "  \"lease_end_date\": \"\",\n"
    "  \"deposit_amount\": \"\",\n"
    "  \"type\": \"rental_agreement\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_PROPERTY_TAX_PROMPT = (
    "Analyse the given Property Tax document and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"owner_name\": \"\",\n"
    "  \"property_address\": \"\",\n"
    "  \"assessment_number\": \"\",\n"
    "  \"tax_amount\": \"\",\n"
    "  \"year\": \"\",\n"
    "  \"type\": \"property_tax\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_SHOP_LICENSE_PROMPT = (
    "Analyse the given Shop & Establishment License and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"shop_name\": \"\",\n"
    "  \"owner_name\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"license_number\": \"\",\n"
    "  \"valid_from\": \"\",\n"
    "  \"valid_to\": \"\",\n"
    "  \"type\": \"shop_license\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_FINANCIAL_STATEMENT_PROMPT = (
    "Analyse the given Financial Statement and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"entity_name\": \"\",\n"
    "  \"period\": \"\",\n"
    "  \"total_revenue\": \"\",\n"
    "  \"total_expenses\": \"\",\n"
    "  \"net_profit\": \"\",\n"
    "  \"total_assets\": \"\",\n"
    "  \"total_liabilities\": \"\",\n"
    "  \"type\": \"financial_statement\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_FORM16_PROMPT = (
    "Analyse the given Form 16 (TDS certificate) and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"employee_name\": \"\",\n"
    "  \"employer_name\": \"\",\n"
    "  \"pan\": \"\",\n"
    "  \"assessment_year\": \"\",\n"
    "  \"gross_salary\": \"\",\n"
    "  \"total_tax_deducted\": \"\",\n"
    "  \"type\": \"form16\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_GST_RETURN_PROMPT = (
    "Analyse the given GST Return document and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"gstin\": \"\",\n"
    "  \"legal_name\": \"\",\n"
    "  \"return_type\": \"\",\n"
    "  \"return_period\": \"\",\n"
    "  \"total_taxable_value\": \"\",\n"
    "  \"total_tax\": \"\",\n"
    "  \"date_of_filing\": \"\",\n"
    "  \"type\": \"gst_return\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_ITR_PROMPT = (
    "Analyse the given Indian Income Tax Return (ITR) document and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"assessee_name\": \"\",\n"
    "  \"pan\": \"\",\n"
    "  \"assessment_year\": \"\",\n"
    "  \"acknowledgement_number\": \"\",\n"
    "  \"gross_total_income\": \"\",\n"
    "  \"total_tax_payable\": \"\",\n"
    "  \"refund\": \"\",\n"
    "  \"type\": \"itr\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_MULTI_DOCUMENT_PROMPT = (
    "Analyse all the documents visible in the image and extract all data found in strict JSON format. "
    "Return an array of document objects, each with a 'type' field identifying the document type. "
    "Return ONLY the JSON array, no extra text.\n"
)

_INSURANCE_PROMPT = (
    "Analyse the given Insurance document and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"policy_number\": \"\",\n"
    "  \"insured_name\": \"\",\n"
    "  \"insurer_name\": \"\",\n"
    "  \"policy_type\": \"\",\n"
    "  \"start_date\": \"\",\n"
    "  \"end_date\": \"\",\n"
    "  \"sum_assured\": \"\",\n"
    "  \"premium\": \"\",\n"
    "  \"type\": \"insurance_document\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)

_RC_PROMPT = (
    "Analyse the given Indian Vehicle Registration Certificate (RC) and extract the following details in strict JSON format:\n"
    "{\n"
    "  \"owner_name\": \"\",\n"
    "  \"registration_number\": \"\",\n"
    "  \"chassis_number\": \"\",\n"
    "  \"engine_number\": \"\",\n"
    "  \"vehicle_class\": \"\",\n"
    "  \"fuel_type\": \"\",\n"
    "  \"registration_date\": \"\",\n"
    "  \"valid_upto\": \"\",\n"
    "  \"address\": \"\",\n"
    "  \"type\": \"vehicle_rc\"\n"
    "}\n"
    "Return ONLY the JSON, no extra text.\n"
)


# ----------------------------
# Module-level PII masking
# ----------------------------
def mask_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive PII fields (PAN, Aadhaar, Voter ID, Account, IFSC).
    This is exported at module level so controllers can use it too."""
    if not isinstance(data, dict):
        return data

    def _mask_str(s: str, visible_chars: int = 4) -> str:
        if not s:
            return s
        val = str(s)
        if len(val) <= visible_chars:
            return "X" * len(val)
        return "X" * (len(val) - visible_chars) + val[-visible_chars:]

    # PAN masking – keep last 4 chars
    if "pan_no" in data and data["pan_no"]:
        data["pan_no"] = _mask_str(str(data["pan_no"]), 4)

    # Aadhaar masking – keep last 4 chars
    if "aadhar_no" in data and data["aadhar_no"]:
        data["aadhar_no"] = _mask_str(str(data["aadhar_no"]).replace(" ", ""), 4)

    # Voter ID masking
    if "voter_id" in data and data["voter_id"]:
        data["voter_id"] = _mask_str(str(data["voter_id"]), 4)

    # Bank Account masking
    for key in ["account_number", "account_no", "bank_account_number", "acc_no", "bank_account"]:
        if key in data and data[key]:
            data[key] = _mask_str(str(data[key]).replace(" ", ""), 4)

    # IFSC masking – show first 4 chars (bank code), mask the rest
    for key in ["ifsc", "ifsc_code", "bank_ifsc"]:
        if key in data and data[key]:
            val = str(data[key])
            if len(val) > 4:
                data[key] = val[:4] + "X" * (len(val) - 4)
            else:
                data[key] = "X" * len(val)

    return data


# ----------------------------
# OCR init
# ----------------------------
_ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

def _ocr_image(file_bytes: bytes) -> str:
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    ocr_result = _ocr_model.ocr(img)
    extracted_text = "\n".join([line[1][1] for line in ocr_result])
    return extracted_text

# ----------------------------
# LLM routing
# ----------------------------
def _send_to_github(content_list: List[Dict[str, Any]], model: str, max_tokens: int, temperature: float) -> str:
    print(f"[DEBUG] Calling GitHub API with model: {model}")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_GITHUB_API_KEY}",
    }
    payload = {
        "model": model,
        "temperature": temperature,
        "top_p": 1,
        "messages": [
            {"role": "user", "content": content_list}
        ],
        "max_tokens": max_tokens,
    }
    resp = requests.post(_GITHUB_API_URL, headers=headers, json=payload, timeout=120)
    print(f"[DEBUG] GitHub API status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"[DEBUG] GitHub API error response: {resp.text}")
        raise RuntimeError(f"GITHUB LLM API error: {resp.text}")
    data = resp.json()
    result = data["choices"][0]["message"]["content"]
    print(f"[DEBUG] GitHub API response length: {len(result)} chars")
    return result

def _send_to_ollama(content_list: List[Dict[str, Any]], model: str, max_tokens: int, temperature: float) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_OLLAMA_API_KEY}",
    }
    payload = {
        "model": model,
        "temperature": temperature,
        "top_p": 1,
        "messages": [
            {"role": "user", "content": content_list}
        ],
        "max_tokens": max_tokens,
    }
    url = f"{_OLLAMA_BASE_URL.rstrip('/')}/chat/completions"
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"OLLAMA LLM API error: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]

def _switch_models(content_list: List[Dict[str, Any]], model: str = _DEFAULT_MODEL, max_tokens: int = 4000, temperature: float = 0.3) -> str:
    if _OCR_LLM_BACKEND == "github":
        return _send_to_github(content_list, model, max_tokens, temperature)
    if _OCR_LLM_BACKEND == "ollama":
        return _send_to_ollama(content_list, _OLLAMA_MODEL, max_tokens, temperature)

    if _GITHUB_API_KEY:
        try:
            return _send_to_github(content_list, model, max_tokens, temperature)
        except Exception as e:
            print(f"GitHub LLM Error: {e}")
            pass
    try:
        return _send_to_ollama(content_list, _OLLAMA_MODEL, max_tokens, temperature)
    except Exception as e:
        print(f"Ollama LLM Error: {e}")
        return ""

# ----------------------------
# Prompt selection
# ----------------------------
def _clean_gpt_json(gpt_output: str) -> str:
    cleaned = re.sub(r"```(?:json)?\n?", "", gpt_output)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()

def _build_prompt(doc_type: str) -> str:
    if doc_type == "ind_pan":
        return _PAN_PROMPT
    if doc_type == "ind_aadhaar":
        return _AADHAAR_PROMPT
    if doc_type == "comp_pan":
        return _COMPANY_PAN_PROMPT
    if doc_type == "ind_aadhar":  # back-compat
        return _AADHAAR_PROMPT
    if doc_type == "ind_gst_certificate":
        return _GST_PROMPT
    if doc_type == "ind_cheque":
        return _CHEQUE_PROMPT
    if doc_type == "ind_voterid":
        return _VOTER_ID_PROMPT
    if doc_type == "ind_driving_license":
        return _DRIVING_LICENSE_PROMPT
    if doc_type == "ind_udyog_aadhaar":
        return _UDYOG_AADHAAR_PROMPT
    if doc_type == "validate_bank_account":
        return _PENNYDROP_PROMPT
    if doc_type == "classify":
        return _CLASSIFY_PROMPT
    if doc_type == "ind_electricity_bill":
       return _EB_BILL_PROMPT
    if doc_type == "water_bill":
       return _WATER_BILL_PROMPT
    if doc_type == "payslip":
       return _PAYS_LIP_PROMPT
    if doc_type == "business_card":
        return _BUSINESS_CARD_PROMPT
    if doc_type == "name_board":
        return _NAME_BOARD_PROMPT
    if doc_type == "rental_agreement":
        return _RENTAL_AGREEMENT_PROMPT
    if doc_type == "property_tax":
        return _PROPERTY_TAX_PROMPT
    if doc_type == "shop_license":
        return _SHOP_LICENSE_PROMPT
    if doc_type == "financial_statement":
        return _FINANCIAL_STATEMENT_PROMPT
    if doc_type == "form16":
        return _FORM16_PROMPT
    if doc_type == "gst_return":
        return _GST_RETURN_PROMPT
    if doc_type == "itr":
        return _ITR_PROMPT
    if doc_type == "multi_document":
        return _MULTI_DOCUMENT_PROMPT
    if doc_type == "insurance_document":
        return _INSURANCE_PROMPT
    if doc_type == "vehicle_rc":
        return _RC_PROMPT

    raise ValueError("Unsupported document type")

# ----------------------------
# Auto-detection
# ----------------------------
def _detect_document_type_from_text(text: str) -> str:
    upper_text = text.upper()
    digits_only = re.sub(r"[^0-9]", "", upper_text)
    alnum_only = re.sub(r"[^A-Z0-9]", "", upper_text)

    if re.search(r"\b\d{12}\b", digits_only):
        return "ind_aadhaar"

    if re.search(r"[A-Z]{5}\d{4}[A-Z]", alnum_only):
        if "COMPANY" in upper_text or "LIMITED" in upper_text or "PRIVATE" in upper_text:
            return "comp_pan"
        return "ind_pan"
    return ""

def _detect_type_from_bytes(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    text_blob = ""
    if ext == "pdf":
        is_text_pdf = False
        extracted_text = ""
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    is_text_pdf = True
                    extracted_text += text + "\n"

    if is_text_pdf:
        # Normal searchable PDF
        content_list = [
            {"type": "text", "text": prompt_template},
            {"type": "text", "text": extracted_text},
        ]
        return _switch_models(content_list)
    else:
        # Scanned PDF → run OCR instead of sending image to LLM
        pages = convert_from_bytes(file_bytes, dpi=300)
        extracted_text = ""
        for page in pages:
            buffered = BytesIO()
            page.save(buffered, format="JPEG")
            ocr_text = _ocr_image(buffered.getvalue())
            extracted_text += ocr_text + "\n"

        content_list = [
            {"type": "text", "text": prompt_template},
            {"type": "text", "text": extracted_text},
        ]
        return _switch_models(content_list)
    return _detect_document_type_from_text(text_blob.upper())

# ----------------------------
# Extraction core
# ----------------------------
def _extract_from_bytes(file_bytes: bytes, filename: str, doc_type: str) -> Any:
    print(f"[DEBUG] _extract_from_bytes called: filename={filename}, doc_type={doc_type}, bytes_len={len(file_bytes)}")
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    prompt_template = _build_prompt(doc_type)
    print(f"[DEBUG] File extension: {ext}, Prompt template length: {len(prompt_template)}")

    def _process_llm_json(json_str: str) -> Any:
        """Parse LLM JSON output, apply PII masking, and return dict."""
        try:
            cleaned = _clean_gpt_json(json_str)
            data = json.loads(cleaned)
            return mask_pii(data)
        except Exception as e:
            print(f"Error masking JSON: {e}")
            return json_str

    if ext == "pdf":
        is_text_pdf = False
        extracted_text = ""
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    is_text_pdf = True
                    extracted_text += text + "\n"

        if is_text_pdf:
            content_list = [
                {"type": "text", "text": prompt_template},
                {"type": "text", "text": extracted_text},
            ]
            raw_json = _switch_models(content_list)
            return _process_llm_json(raw_json)
        else:
            pages = convert_from_bytes(file_bytes, dpi=300)
            results: List[Dict[str, Any]] = []
            for i, page in enumerate(pages):
                buffered = BytesIO()
                page.save(buffered, format="JPEG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                content_list = [
                    {"type": "text", "text": prompt_template},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ]
                raw_json = _switch_models(content_list)
                masked_data = _process_llm_json(raw_json)
                # Convert back to string for consistency with existing list structure
                masked_str = json.dumps(masked_data) if isinstance(masked_data, dict) else str(masked_data)
                results.append({"page": i + 1, "json": masked_str})
            return results

    print(f"[DEBUG] Processing as image (not PDF)")
    image_base64 = base64.b64encode(file_bytes).decode("utf-8")
    print(f"[DEBUG] Image base64 length: {len(image_base64)}")
    content_list = [
        {"type": "text", "text": prompt_template},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
    ]
    result = _switch_models(content_list)
    print(f"[DEBUG] _switch_models returned: {result[:200] if result else 'EMPTY'}...")
    return _process_llm_json(result)

def _extract_from_url(file_url: str, doc_type: str) -> Any:
    resp = requests.get(file_url, timeout=30)
    resp.raise_for_status()
    filename = file_url.split("/")[-1]
    return _extract_from_bytes(resp.content, filename, doc_type)

# ----------------------------
# Public API
# ----------------------------
def extract_documents(doc_type: str, documents: List[str]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for doc in documents:
        try:
            if doc.startswith("http://") or doc.startswith("https://"):
                if doc_type == "auto":
                    resp = requests.get(doc, timeout=30)
                    resp.raise_for_status()
                    filename = doc.split("/")[-1]
                    detected = _detect_type_from_bytes(resp.content, filename)
                    if not detected:
                        raise ValueError("unsupported_document: not Aadhaar / PAN")
                    raw = _extract_from_bytes(resp.content, filename, detected)
                else:
                    raw = _extract_from_url(doc, doc_type)
            else:
                if doc.startswith("data:"):
                    b64_part = doc.split(",", 1)[1] if "," in doc else ""
                else:
                    b64_part = doc
                file_bytes = base64.b64decode(b64_part)
                filename = "upload.pdf" if file_bytes[:4] == b"%PDF" else "upload.jpg"
                if doc_type == "auto":
                    detected = _detect_type_from_bytes(file_bytes, filename)
                    if not detected:
                        raise ValueError("unsupported_document: not Aadhaar / PAN")
                    raw = _extract_from_bytes(file_bytes, filename, detected)
                else:
                    raw = _extract_from_bytes(file_bytes, filename, doc_type)

            if isinstance(raw, list):
                merged: Dict[str, Any] = {}
                for r in raw:
                    # r may be a dict (already masked) or a string
                    if isinstance(r, dict):
                        page_data = r.get("json", r)
                        if isinstance(page_data, str):
                            try:
                                page_data = json.loads(_clean_gpt_json(page_data))
                            except Exception:
                                page_data = {}
                        if isinstance(page_data, dict):
                            merged.update({k: v for k, v in page_data.items() if v not in (None, "")})
                    elif isinstance(r, str):
                        try:
                            page_data = json.loads(_clean_gpt_json(r))
                            if isinstance(page_data, dict):
                                merged.update({k: v for k, v in page_data.items() if v not in (None, "")})
                        except Exception:
                            pass
                # Apply masking on the final merged dict
                results.append(mask_pii(merged) if merged else {"error": "unable_to_parse"})
            elif isinstance(raw, dict):
                # Already processed by _process_llm_json, just append
                results.append(raw)
            else:
                # raw is a string (shouldn't happen often but handle gracefully)
                cleaned = _clean_gpt_json(str(raw))
                try:
                    parsed = json.loads(cleaned)
                    results.append(mask_pii(parsed) if isinstance(parsed, dict) else parsed)
                except json.JSONDecodeError:
                    results.append({"raw": cleaned})
        except Exception as e:
            results.append({"error": str(e)})
    return results
