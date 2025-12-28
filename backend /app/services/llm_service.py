import os
import json
import requests
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_url = "https://models.github.ai/inference/chat/completions"
        self.api_key = os.getenv("GITHUB_INFERENCE_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def compare_data(self, extracted_data: Dict, reference_data: Dict) -> Dict:
        """
        Compare extracted invoice data with reference data using LLM, returning a unified object with invoice_details and comparison_results.
        """
        try:
            # The unified template structure for the LLM to fill
            template = {
                "invoice_details": {
                    "invoice_number": {"label": "Invoice Number", "value": ""},
                    "invoice_date": {"label": "Invoice Date", "value": ""},
                    "irn_number": {"label": "IRN Number", "value": ""},
                    "ack_number": {"label": "Ack Number", "value": ""},
                    "ack_date": {"label": "Ack Date", "value": ""},
                    "ack_status": {"label": "Ack Status", "value": ""}
                },
                "comparison_results": [
                    {"field": "invoice_date", "label": "Invoice Date", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "vendor_name", "label": "Vendor Name", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "vendor_gstin", "label": "Vendor GSTIN", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "buyer_name", "label": "Buyer Name", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "buyer_gstin", "label": "Buyer GSTIN", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "taxable_amount", "label": "Taxable Amount", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "sgst_percent", "label": "SGST %", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "sgst_amount", "label": "SGST Amount", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "cgst_percent", "label": "CGST %", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "cgst_amount", "label": "CGST Amount", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "igst_percent", "label": "IGST %", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "igst_amount", "label": "IGST Amount", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""},
                    {"field": "total_amount", "label": "Total Amount", "extracted_value": "", "expected_value": "", "match": None, "llm_analysis": ""}
                ]
            }
            system_prompt = (
                "You are an expert in analyzing invoice data. "
                "Fill in the following JSON template using the extracted invoice data and the reference data. "
                "For 'invoice_details', fill in the 'value' for each field from the extracted invoice. "
                "For each item in 'comparison_results', fill in 'extracted_value', 'expected_value', 'match' (true/false/null), and a brief 'llm_analysis'. "
                "Return only the completed JSON object, with no extra text, markdown, or code fences, or any extra commentary—just the JSON."
            )
            user_prompt = (
                f"Extracted Data:\n{json.dumps(extracted_data, indent=2)}\n\n"
                f"Reference Data:\n{json.dumps(reference_data, indent=2)}\n\n"
                f"JSON Template:\n{json.dumps(template, indent=2)}"
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = await self._call_llm_api(messages)
            print("LLM full API response (compare):", response)
            content = response["choices"][0]["message"]["content"]
            print("LLM raw response content (compare):", content)
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"Error in LLM comparison: {e}")
            raise Exception(f"Error in LLM comparison: {str(e)}")

    def _prepare_comparison_prompt(self, extracted_data: Dict, reference_data: Dict) -> List[Dict]:
        """
        Prepare the prompt for LLM analysis
        """
        system_prompt = {
            "role": "system",
            "content": """You are an expert in analyzing invoice data. Your task is to compare extracted invoice data with reference data and identify any discrepancies. Consider the following aspects:
1. Field value matching
2. Format consistency
3. Business logic validation
4. Context-aware comparison
Provide detailed analysis with confidence scores."""
        }

        user_prompt = {
            "role": "user",
            "content": f"""Please compare the following extracted invoice data with reference data and identify any discrepancies:

Extracted Data:
{json.dumps(extracted_data, indent=2)}

Reference Data:
{json.dumps(reference_data, indent=2)}

Provide your analysis in the following JSON format:
{{
    "discrepancies": [
        {{
            "field": "field_name",
            "extracted_value": "value from extracted data",
            "reference_value": "value from reference data",
            "confidence": 0.95,
            "llm_analysis": "detailed analysis of the discrepancy",
            "severity": "high|medium|low"
        }}
    ],
    "summary": "Overall summary of findings",
    "confidence_score": 0.95
}}"""
        }

        return [system_prompt, user_prompt]

    async def _call_llm_api(self, messages: List[Dict]) -> Dict:
        """
        Call the GitHub Inference API
        """
        payload = {
            "model": "openai/gpt-4.1",
            "temperature": 1,
            "top_p": 1,
            "messages": messages
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.text}")

        return response.json()

    def _process_llm_response(self, response: Dict) -> List[Dict]:
        """
        Process and validate the LLM response
        """
        try:
            # Extract the content from the LLM response
            content = response["choices"][0]["message"]["content"]
            
            # Parse the JSON response
            result = json.loads(content)
            
            # Validate the response structure
            if not isinstance(result, dict) or "discrepancies" not in result:
                raise ValueError("Invalid response format from LLM")
            
            return result["discrepancies"]

        except Exception as e:
            raise Exception(f"Error processing LLM response: {str(e)}")

    async def llm_extract(self, messages: List[Dict]) -> Dict:
        response = await self._call_llm_api(messages)
        print("LLM full API response:", response)
        try:
            content = response["choices"][0]["message"]["content"]
            print("LLM raw response content:", content)
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"Error parsing LLM extraction response: {e}")
            raise Exception(f"Error parsing LLM extraction response: {str(e)}") 