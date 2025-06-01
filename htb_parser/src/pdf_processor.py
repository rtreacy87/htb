# src/pdf_processor.py
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict

class PDFProcessor:
    """
    A class to handle PDF text extraction and basic processing.
    
    This is like a smart PDF reader that can extract text and 
    tell us information about the document.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.current_document = None
        self.document_path = None

    def load_pdf(self, pdf_path: str) -> bool:
        """
        Load a PDF file for processing.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if successful, False if there was an error
        """
        try:
            self._convert_string_path(pdf_path)
            if self._check_if_file_exists():
                self._load_pdf(pdf_path)
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ Error loading PDF: {e}")
            return False

    def _convert_string_path(self, pdf_path: str):
        """Convert string path to Path object."""
        if not pdf_path or pdf_path.strip() == "":
            self.document_path = None
            return
        self.document_path = Path(pdf_path)

    def _check_if_file_exists(self):
        """Check if the PDF file exists at the specified path."""
        if not self.document_path:
            return False
        return self.document_path.exists()

    def _load_pdf(self, pdf_path: str):
        """Load the PDF document using PyMuPDF."""
        self.current_document = fitz.open(self.document_path)
        if not self.document_path or not self.document_path.name:
            print("❌ Error: Invalid document path")
            return
        print(f"✅ Successfully loaded PDF: {self.document_path.name}")
        print(f"   Pages: {len(self.current_document)}")

    
    def get_document_info(self) -> Dict:
        """
        Get basic information about the loaded PDF.
        
        Returns:
            Dictionary with document metadata
      """
        if not self.current_document:
            return {"error": "No document loaded"}
        
        # Get metadata from the PDF
        metadata = self.current_document.metadata
        
        return {
            "title": metadata.get("title", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "subject": metadata.get("subject", "Unknown"),
            "creator": metadata.get("creator", "Unknown"),
            "pages": len(self.current_document),
            "file_size": self.document_path.stat().st_size if self.document_path else 0
        }

    def extract_text_from_page(self, page_number: int) -> str:
        """
        Extract text from a specific page.
        
        Args:
            page_number: Page number (0-based)
            
        Returns:
            Extracted text as string
        """
        if not self.current_document:
            return "Error: No document loaded"
        
        if page_number >= len(self.current_document):
            return f"Error: Page {page_number} doesn't exist"
        
        try:
            page = self._get_page(page_number)
            text = self._extract_text_from_page(page)
            return text
        except Exception as e:
            return f"Error extracting text from page {page_number}: {e}"
    
    def _get_page(self, page_number: int):
        """Get the page object from the document."""
        if not self.current_document:
            return None
        return self.current_document[page_number]
    
    def _extract_text_from_page(self, page):
        """Extract text from a page object."""
        return page.get_text()

    def extract_all_text(self) -> str:
        """
        Extract text from all pages in the document.
        
        Returns:
            All text combined as a single string
        """
        if not self.current_document:
            return "Error: No document loaded"
        
        all_text = []
        
        for page_num in range(len(self.current_document)):
            self._report_progress(page_num)
            
            page_text = self.extract_text_from_page(page_num)
            
            # Add page separator and text
            all_text.append(self._format_page_separator(page_num))
            all_text.append(page_text)
        
        return "\n".join(all_text)

    def _report_progress(self, page_num: int):
        """Report progress during text extraction."""
        print(f"Processing page {page_num + 1}...")

    def _format_page_separator(self, page_num: int) -> str:
        """Format the page separator for extracted text."""
        return f"\n--- Page {page_num + 1} ---\n"    

    def close_document(self):
        """Close the current document and free memory."""
        if self.current_document:
            self.current_document.close()
            self.current_document = None
            print("📄 Document closed")

    def get_page_info(self, page_number: int) -> Dict:
        """
        Get detailed information about a specific page.
        
        Args:
            page_number: Page number (0-based)
            
        Returns:
            Dictionary with page information
        """
        if not self.current_document:
            return {"error": "No document loaded"}
        
        if page_number >= len(self.current_document):
            return {"error": f"Page {page_number} doesn't exist"}
        
        try:
            page = self.current_document[page_number]
            
            # Get page dimensions
            rect = page.rect
            
            # Count text blocks
            text_dict = page.get_text("dict")
            block_count = len(text_dict["blocks"])
            
            return {
                "page_number": page_number,
                "width": rect.width,
                "height": rect.height,
                "text_blocks": block_count,
                "has_images": len(page.get_images()) > 0,
                "image_count": len(page.get_images())
            }
            
        except Exception as e:
            return {"error": f"Error getting page info: {e}"}
