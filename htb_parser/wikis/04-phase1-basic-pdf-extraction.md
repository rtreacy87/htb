# Phase 1: Basic PDF Text Extraction

## What We're Building in This Phase

In this phase, we'll create the foundation of our parser - the ability to extract text from PDF files. Think of this as teaching our program how to "read" PDFs.

## Learning Objectives

By the end of this phase, you'll have:
- A working PDF text extractor
- Understanding of how PDFs store text
- A simple command-line tool to test extraction
- The foundation for more advanced features

## Understanding PDF Text Extraction

### How PDFs Store Text

PDFs are like digital documents that remember exactly where each letter should appear on a page. Unlike a simple text file, PDFs store:
- Text content
- Font information
- Positioning data
- Images and graphics
- Metadata (title, author, etc.)

### Why We Need Special Tools

You can't just open a PDF like a text file because the text is stored in a complex format. We need libraries like PyMuPDF to translate the PDF format into plain text we can work with.

## Step 1: Create the PDF Processor Module

Let's create our first component! In your `src` folder, create a file called `pdf_processor.py`:

```python
# src/pdf_processor.py
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional

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
            # Convert string path to Path object for better handling
            self.document_path = Path(pdf_path)
            
            # Check if file exists
            if not self.document_path.exists():
                print(f"Error: File {pdf_path} not found!")
                return False
            
            # Open the PDF document
            self.current_document = fitz.open(pdf_path)
            print(f"✅ Successfully loaded PDF: {self.document_path.name}")
            print(f"   Pages: {len(self.current_document)}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading PDF: {e}")
            return False
    
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
            # Get the page
            page = self.current_document[page_number]
            
            # Extract text
            text = page.get_text()
            
            return text
            
        except Exception as e:
            return f"Error extracting text from page {page_number}: {e}"
    
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
            print(f"Processing page {page_num + 1}...")
            
            page_text = self.extract_text_from_page(page_num)
            
            # Add page separator for clarity
            all_text.append(f"\n--- Page {page_num + 1} ---\n")
            all_text.append(page_text)
        
        return "\n".join(all_text)
    
    def close_document(self):
        """Close the current document and free memory."""
        if self.current_document:
            self.current_document.close()
            self.current_document = None
            print("📄 Document closed")
```

## Step 2: Create a Simple Test Script

Let's create a simple script to test our PDF processor. Create `test_extraction.py` in your project root:

```python
# test_extraction.py
from src.pdf_processor import PDFProcessor

def test_pdf_extraction():
    """Simple test function for our PDF processor."""
    
    # Create a PDF processor instance
    processor = PDFProcessor()
    
    # Ask user for PDF file path
    pdf_path = input("Enter the path to your PDF file: ")
    
    # Try to load the PDF
    if processor.load_pdf(pdf_path):
        # Show document information
        info = processor.get_document_info()
        print("\n📋 Document Information:")
        print(f"   Title: {info['title']}")
        print(f"   Author: {info['author']}")
        print(f"   Pages: {info['pages']}")
        print(f"   File size: {info['file_size']} bytes")
        
        # Ask if user wants to extract all text or just one page
        choice = input("\nExtract (a)ll pages or (s)ingle page? [a/s]: ").lower()
        
        if choice == 's':
            page_num = int(input("Which page number (starting from 1)? ")) - 1
            text = processor.extract_text_from_page(page_num)
            print(f"\n📄 Text from page {page_num + 1}:")
            print("-" * 50)
            print(text)
        else:
            print("\n📄 Extracting all text...")
            text = processor.extract_all_text()
            
            # Save to file
            output_file = "extracted_text.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"✅ Text saved to {output_file}")
            print(f"   Total characters: {len(text)}")
        
        # Clean up
        processor.close_document()
    
    else:
        print("❌ Failed to load PDF file")

if __name__ == "__main__":
    test_pdf_extraction()
```

## Step 3: Test Your PDF Extractor

### Find a Test PDF

You'll need a PDF file to test with. You can:
1. Use any PDF you have on your computer
2. Download a sample HTB writeup PDF
3. Create a simple PDF with some text

### Run the Test

1. Make sure your virtual environment is active
2. Navigate to your project folder
3. Run the test:

```bash
python test_extraction.py
```

### What You Should See

```
Enter the path to your PDF file: /path/to/your/file.pdf
✅ Successfully loaded PDF: your_file.pdf
   Pages: 5

📋 Document Information:
   Title: HTB Writeup - Machine Name
   Author: Security Researcher
   Pages: 5
   File size: 1234567 bytes

Extract (a)ll pages or (s)ingle page? [a/s]: a

📄 Extracting all text...
Processing page 1...
Processing page 2...
Processing page 3...
Processing page 4...
Processing page 5...
✅ Text saved to extracted_text.txt
   Total characters: 15432
📄 Document closed
```

## Step 4: Understanding the Output

Open the `extracted_text.txt` file that was created. You'll notice:

### Good Things:
- Text is extracted successfully
- Page breaks are clearly marked
- Most content is readable

### Issues You Might See:
- Formatting is lost (no bold, italic, etc.)
- Code blocks might not be clearly separated
- Some text might be in wrong order (multi-column layouts)
- Special characters might look strange

**Don't worry!** These issues are normal at this stage. We'll fix them in later phases.

## Step 5: Add Error Handling and Improvements

Let's make our processor more robust. Add this method to your `PDFProcessor` class:

```python
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
```

## Understanding What We've Built

### The PDFProcessor Class

Our `PDFProcessor` is like a smart PDF reader that can:
- **Load PDFs**: Open and validate PDF files
- **Extract text**: Get readable text from any page
- **Provide metadata**: Tell us about the document
- **Handle errors**: Gracefully deal with problems

### Key Methods Explained

1. **`load_pdf()`**: Opens a PDF file and prepares it for processing
2. **`extract_text_from_page()`**: Gets text from one specific page
3. **`extract_all_text()`**: Gets text from the entire document
4. **`get_document_info()`**: Provides metadata about the PDF
5. **`close_document()`**: Cleans up memory when done

## Common Issues and Solutions

### Issue: "Module not found" Error
**Solution**: Make sure your virtual environment is active and PyMuPDF is installed

### Issue: "File not found" Error
**Solution**: Check the file path - use forward slashes (/) even on Windows

### Issue: Extracted text looks garbled
**Solution**: This is normal for some PDFs. We'll improve this in later phases

### Issue: Very slow extraction
**Solution**: Large PDFs take time. This is normal for the basic version

## What We've Accomplished

🎉 **Congratulations!** You've built a working PDF text extractor that can:
- Load any PDF file
- Extract text from individual pages or entire documents
- Provide useful metadata about the document
- Handle errors gracefully
- Save extracted text to files

## What's Next?

In Phase 2, we'll make our extractor much smarter by adding:
- Content type recognition (identifying commands, code, headings)
- Better text structure analysis
- Pattern matching for HTB-specific content
- Improved handling of complex layouts

The foundation you've built here will support all these advanced features!

---

[← Previous: Development Environment Setup](03-development-environment-setup.md) | [Next: Phase 2 - Content Recognition →](05-phase2-content-recognition.md)
