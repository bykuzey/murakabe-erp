"""
MinimalERP - OCR Service

Automatic document extraction using Tesseract OCR and OpenAI Vision API.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re
import io
from PIL import Image
import pytesseract

from core.services.ai_base import AIServiceBase
from core.config import settings

logger = logging.getLogger(__name__)


class OCRService(AIServiceBase):
    """
    OCR Service for automatic invoice/receipt extraction.

    Features:
    - Image preprocessing
    - Text extraction with Tesseract
    - Structured data extraction with regex/AI
    - Turkish language support
    """

    def __init__(self):
        super().__init__(model_name="ocr_extractor")
        self.tesseract_config = '--oem 3 --psm 6 -l tur+eng'

    async def train(self, data, **kwargs):
        """OCR doesn't require training"""
        logger.info("OCR service doesn't require training")
        return {"message": "OCR service ready"}

    async def predict(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Extract structured data from document image.

        Args:
            data: PIL Image or image bytes

        Returns:
            Extracted invoice data
        """
        try:
            # Preprocess image
            image = self._preprocess_image(data)

            # Extract text with Tesseract
            text = self._extract_text(image)

            # Parse structured data
            extracted_data = self._parse_invoice_data(text)

            return {
                "success": True,
                "data": extracted_data,
                "raw_text": text,
                "confidence": extracted_data.get("confidence", 0.0)
            }

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    def _preprocess_image(self, image_data: Any) -> Image.Image:
        """
        Preprocess image for better OCR results.

        Steps:
        - Convert to grayscale
        - Increase contrast
        - Remove noise
        - Resize if needed
        """
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        else:
            image = image_data

        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')

        # Resize if too large
        max_size = 3000
        if image.width > max_size or image.height > max_size:
            ratio = min(max_size / image.width, max_size / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    def _extract_text(self, image: Image.Image) -> str:
        """Extract text from image using Tesseract"""
        try:
            text = pytesseract.image_to_string(
                image,
                config=self.tesseract_config
            )
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return ""

    def _parse_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        Parse structured invoice data from extracted text.

        Extracts:
        - Invoice number
        - Date
        - Company info
        - Amounts
        - Tax info
        """
        data = {
            "invoice_number": self._extract_invoice_number(text),
            "invoice_date": self._extract_date(text),
            "company_info": self._extract_company_info(text),
            "amounts": self._extract_amounts(text),
            "tax_info": self._extract_tax_info(text),
            "confidence": 0.0
        }

        # Calculate confidence based on extracted fields
        filled_fields = sum(1 for v in data.values() if v)
        data["confidence"] = filled_fields / 6.0  # 6 main fields

        return data

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number"""
        patterns = [
            r'(?:FATURA|INVOICE)\s*(?:NO|NUM|#)?\s*:?\s*([A-Z0-9]+)',
            r'(?:BELGE|DOCUMENT)\s*(?:NO)?\s*:?\s*([A-Z0-9]+)',
            r'(?:SERI|SERIES)?\s*:?\s*([A-Z]+)\s*(?:NO)?\s*:?\s*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.lastindex == 1 else f"{match.group(1)}{match.group(2)}"

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract invoice date"""
        patterns = [
            r'(\d{2})[./](\d{2})[./](\d{4})',  # DD.MM.YYYY or DD/MM/YYYY
            r'(\d{4})[./](\d{2})[./](\d{2})',  # YYYY.MM.DD
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
                else:  # DD-MM-YYYY
                    return f"{groups[2]}-{groups[1]}-{groups[0]}"

        return None

    def _extract_company_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract company information"""
        info = {
            "name": None,
            "tax_number": None,
            "tax_office": None
        }

        # Tax number (VKN - 10 digits)
        vkn_match = re.search(r'(?:VKN|V\.K\.N\.|VERGI\s*NO)\s*:?\s*(\d{10})', text, re.IGNORECASE)
        if vkn_match:
            info["tax_number"] = vkn_match.group(1)

        # Tax office
        tax_office_match = re.search(r'(?:VERGI\s*DAIRES[İI])\s*:?\s*([A-ZÇĞİÖŞÜ\s]+)', text, re.IGNORECASE)
        if tax_office_match:
            info["tax_office"] = tax_office_match.group(1).strip()

        return info

    def _extract_amounts(self, text: str) -> Dict[str, Optional[float]]:
        """Extract monetary amounts"""
        amounts = {
            "subtotal": None,
            "vat": None,
            "total": None
        }

        # Common patterns for amounts
        # Look for patterns like "TOPLAM: 1.234,56 TL"
        patterns = {
            "total": r'(?:TOPLAM|TOTAL|GENEL\s*TOPLAM)\s*:?\s*([\d.,]+)',
            "subtotal": r'(?:ARA\s*TOPLAM|SUBTOTAL|NET)\s*:?\s*([\d.,]+)',
            "vat": r'(?:KDV|VAT)\s*:?\s*([\d.,]+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                # Convert Turkish number format (1.234,56) to float
                amount_str = amount_str.replace('.', '').replace(',', '.')
                try:
                    amounts[key] = float(amount_str)
                except ValueError:
                    pass

        return amounts

    def _extract_tax_info(self, text: str) -> Dict[str, Any]:
        """Extract tax information"""
        tax_info = {
            "vat_rate": None,
            "withholding_rate": None
        }

        # VAT rate
        vat_match = re.search(r'%\s*(\d+)\s*KDV', text, re.IGNORECASE)
        if vat_match:
            tax_info["vat_rate"] = int(vat_match.group(1))

        # Withholding (Tevkifat)
        withholding_match = re.search(r'TEVKIFAT\s*:?\s*%?\s*(\d+)', text, re.IGNORECASE)
        if withholding_match:
            tax_info["withholding_rate"] = int(withholding_match.group(1))

        return tax_info

    async def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from file path.

        Args:
            file_path: Path to image/PDF file

        Returns:
            Extracted data
        """
        try:
            image = Image.open(file_path)
            return await self.predict(image)
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def extract_with_openai(self, image_data: Any) -> Dict[str, Any]:
        """
        Enhanced extraction using OpenAI Vision API.

        This provides better accuracy but requires API key.
        Falls back to Tesseract if OpenAI is not available.
        """
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not set, using Tesseract only")
            return await self.predict(image_data)

        try:
            import openai
            import base64

            # Convert image to base64
            if isinstance(image_data, bytes):
                image_b64 = base64.b64encode(image_data).decode('utf-8')
            else:
                buffer = io.BytesIO()
                image_data.save(buffer, format='PNG')
                image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # Call OpenAI Vision API
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Extract invoice information from this image in JSON format:
                                {
                                    "invoice_number": "...",
                                    "invoice_date": "YYYY-MM-DD",
                                    "company_name": "...",
                                    "tax_number": "...",
                                    "tax_office": "...",
                                    "subtotal": 0.0,
                                    "vat_amount": 0.0,
                                    "vat_rate": 0,
                                    "total": 0.0
                                }
                                Return only valid JSON."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            # Parse JSON response
            import json
            result_text = response.choices[0].message.content
            extracted_data = json.loads(result_text)

            return {
                "success": True,
                "data": extracted_data,
                "confidence": 0.95,  # High confidence with GPT-4 Vision
                "method": "openai_vision"
            }

        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}, falling back to Tesseract")
            return await self.predict(image_data)
