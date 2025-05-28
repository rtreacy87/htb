# Phase 4: Advanced Features

## What We're Adding in This Phase

Now that we have a working parser, let's make it production-ready with advanced features that handle real-world challenges like image-heavy PDFs, complex layouts, and batch processing.

## Learning Objectives

By the end of this phase, you'll have:
- OCR integration for reading text from images
- Multi-column layout handling
- Batch processing capabilities
- Quality validation and error correction
- Performance optimizations

## Advanced Feature 1: OCR Integration

### Why Do We Need OCR?

Many HTB writeups contain screenshots with important information:
- Terminal output as images
- Code snippets in screenshots
- Network diagrams with text labels
- Tool output captured as images

### Setting Up OCR

First, let's enhance our PDF processor with OCR capabilities. Create `src/ocr_processor.py`:

```python
# src/ocr_processor.py
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from typing import List, Dict, Tuple

class OCRProcessor:
    """
    Handles OCR (Optical Character Recognition) for extracting text from images.
    
    This is like having super-powered eyes that can read text from pictures!
    """
    
    def __init__(self):
        """Initialize OCR processor with configuration."""
        self.setup_ocr_config()
    
    def setup_ocr_config(self):
        """Configure OCR settings for better accuracy."""
        
        # OCR configuration for different content types
        self.ocr_configs = {
            "default": "--oem 3 --psm 6",  # Uniform block of text
            "terminal": "--oem 3 --psm 4",  # Single column of text
            "code": "--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`",
            "numbers": "--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789.",
        }
        
        # Confidence threshold for OCR results
        self.confidence_threshold = 60
    
    def extract_images_from_pdf(self, pdf_document, page_number: int) -> List[Dict]:
        """
        Extract all images from a specific PDF page.
        
        Args:
            pdf_document: PyMuPDF document object
            page_number: Page number to extract images from
            
        Returns:
            List of image information dictionaries
        """
        page = pdf_document[page_number]
        image_list = page.get_images()
        
        extracted_images = []
        
        for img_index, img in enumerate(image_list):
            try:
                # Get image data
                xref = img[0]
                pix = fitz.Pixmap(pdf_document, xref)
                
                # Convert to PIL Image
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("ppm")
                    pil_image = Image.open(io.BytesIO(img_data))
                else:  # CMYK
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix.tobytes("ppm")
                    pil_image = Image.open(io.BytesIO(img_data))
                
                # Get image position and size
                img_rect = page.get_image_rects(xref)[0] if page.get_image_rects(xref) else None
                
                extracted_images.append({
                    "index": img_index,
                    "image": pil_image,
                    "position": img_rect,
                    "size": (pil_image.width, pil_image.height),
                    "xref": xref
                })
                
                pix = None  # Free memory
                
            except Exception as e:
                print(f"⚠️ Error extracting image {img_index}: {e}")
                continue
        
        return extracted_images
    
    def preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Resize if too small (OCR works better on larger images)
        width, height = image.size
        if width < 300 or height < 100:
            scale_factor = max(300/width, 100/height, 2.0)
            new_size = (int(width * scale_factor), int(height * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def extract_text_from_image(self, image: Image.Image, content_type: str = "default") -> Dict:
        """
        Extract text from an image using OCR.
        
        Args:
            image: PIL Image object
            content_type: Type of content expected (affects OCR config)
            
        Returns:
            Dictionary with extracted text and confidence
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image_for_ocr(image)
            
            # Get OCR configuration
            config = self.ocr_configs.get(content_type, self.ocr_configs["default"])
            
            # Extract text with confidence data
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                config=config, 
                output_type=pytesseract.Output.DICT
            )
            
            # Filter out low-confidence text
            filtered_text = []
            total_confidence = 0
            valid_words = 0
            
            for i, confidence in enumerate(ocr_data['conf']):
                if int(confidence) > self.confidence_threshold:
                    text = ocr_data['text'][i].strip()
                    if text:
                        filtered_text.append(text)
                        total_confidence += int(confidence)
                        valid_words += 1
            
            # Calculate average confidence
            avg_confidence = total_confidence / valid_words if valid_words > 0 else 0
            
            # Join text
            extracted_text = ' '.join(filtered_text)
            
            return {
                "text": extracted_text,
                "confidence": avg_confidence,
                "word_count": valid_words,
                "success": len(extracted_text) > 0
            }
            
        except Exception as e:
            return {
                "text": "",
                "confidence": 0,
                "word_count": 0,
                "success": False,
                "error": str(e)
            }
    
    def detect_content_type_from_image(self, image: Image.Image) -> str:
        """
        Try to detect what type of content an image contains.
        
        Args:
            image: PIL Image object
            
        Returns:
            Detected content type
        """
        # Quick OCR to analyze content
        try:
            sample_text = pytesseract.image_to_string(image, config="--psm 6")[:200]
            sample_lower = sample_text.lower()
            
            # Check for terminal/command patterns
            if any(term in sample_lower for term in ["$", "#", "root@", "user@", "nmap", "gobuster"]):
                return "terminal"
            
            # Check for code patterns
            if any(term in sample_lower for term in ["def ", "function", "import", "<?php", "{"]):
                return "code"
            
            # Check for numbers/data
            if len([c for c in sample_text if c.isdigit()]) / len(sample_text) > 0.3:
                return "numbers"
            
            return "default"
            
        except:
            return "default"
    
    def process_pdf_with_ocr(self, pdf_document, page_number: int) -> List[Dict]:
        """
        Process a PDF page and extract text from all images using OCR.
        
        Args:
            pdf_document: PyMuPDF document object
            page_number: Page number to process
            
        Returns:
            List of OCR results for each image
        """
        print(f"🔍 Processing images on page {page_number + 1} with OCR...")
        
        # Extract images
        images = self.extract_images_from_pdf(pdf_document, page_number)
        
        if not images:
            print(f"   No images found on page {page_number + 1}")
            return []
        
        ocr_results = []
        
        for img_data in images:
            print(f"   Processing image {img_data['index'] + 1}/{len(images)}...")
            
            # Detect content type
            content_type = self.detect_content_type_from_image(img_data['image'])
            
            # Extract text
            result = self.extract_text_from_image(img_data['image'], content_type)
            
            # Add metadata
            result.update({
                "image_index": img_data['index'],
                "content_type": content_type,
                "image_size": img_data['size'],
                "position": img_data['position']
            })
            
            ocr_results.append(result)
            
            if result['success']:
                print(f"   ✅ Extracted {result['word_count']} words (confidence: {result['confidence']:.1f}%)")
            else:
                print(f"   ❌ OCR failed: {result.get('error', 'Unknown error')}")
        
        return ocr_results
```

## Advanced Feature 2: Enhanced PDF Processor

Let's update our PDF processor to integrate OCR. Add these methods to your `PDFProcessor` class:

```python
# Add to src/pdf_processor.py

from src.ocr_processor import OCRProcessor

class PDFProcessor:
    # ... existing code ...
    
    def __init__(self):
        """Initialize the PDF processor with OCR support."""
        self.current_document = None
        self.document_path = None
        self.ocr_processor = OCRProcessor()
        self.use_ocr = True  # Enable OCR by default
    
    def extract_text_with_ocr(self, page_number: int) -> Dict:
        """
        Extract text from a page using both direct extraction and OCR.
        
        Args:
            page_number: Page number (0-based)
            
        Returns:
            Dictionary with combined text extraction results
        """
        if not self.current_document:
            return {"error": "No document loaded"}
        
        # Get direct text extraction
        direct_text = self.extract_text_from_page(page_number)
        
        # Get OCR text if enabled
        ocr_results = []
        if self.use_ocr:
            ocr_results = self.ocr_processor.process_pdf_with_ocr(
                self.current_document, page_number
            )
        
        # Combine results
        combined_text = direct_text
        
        if ocr_results:
            ocr_text_blocks = []
            for result in ocr_results:
                if result['success'] and result['text'].strip():
                    ocr_text_blocks.append(f"\n--- OCR Text from Image {result['image_index'] + 1} ---")
                    ocr_text_blocks.append(result['text'])
            
            if ocr_text_blocks:
                combined_text += "\n\n" + "\n".join(ocr_text_blocks)
        
        return {
            "direct_text": direct_text,
            "ocr_results": ocr_results,
            "combined_text": combined_text,
            "has_images": len(ocr_results) > 0
        }
    
    def get_page_analysis(self, page_number: int) -> Dict:
        """
        Get comprehensive analysis of a page including text and images.
        
        Args:
            page_number: Page number (0-based)
            
        Returns:
            Dictionary with page analysis
        """
        if not self.current_document:
            return {"error": "No document loaded"}
        
        page = self.current_document[page_number]
        
        # Basic page info
        rect = page.rect
        images = page.get_images()
        
        # Text analysis
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])
        
        # Count different types of blocks
        text_blocks = 0
        image_blocks = 0
        
        for block in blocks:
            if "lines" in block:
                text_blocks += 1
            else:
                image_blocks += 1
        
        return {
            "page_number": page_number,
            "dimensions": {"width": rect.width, "height": rect.height},
            "text_blocks": text_blocks,
            "image_blocks": image_blocks,
            "total_images": len(images),
            "layout_complexity": "high" if len(blocks) > 20 else "medium" if len(blocks) > 10 else "low"
        }
```

## Advanced Feature 3: Batch Processing

Create `src/batch_processor.py` for processing multiple PDFs:

```python
# src/batch_processor.py
import os
from pathlib import Path
from typing import List, Dict
import time
from src.pdf_processor import PDFProcessor
from src.content_analyzer import ContentAnalyzer
from src.markdown_generator import MarkdownGenerator

class BatchProcessor:
    """
    Processes multiple PDF files in batch mode.
    
    This is like having a factory that can process many PDFs automatically!
    """
    
    def __init__(self):
        """Initialize batch processor."""
        self.pdf_processor = PDFProcessor()
        self.content_analyzer = ContentAnalyzer()
        self.markdown_generator = MarkdownGenerator()
        
        # Statistics tracking
        self.processed_files = 0
        self.failed_files = 0
        self.total_processing_time = 0
    
    def find_pdf_files(self, directory: str) -> List[Path]:
        """
        Find all PDF files in a directory and subdirectories.
        
        Args:
            directory: Directory path to search
            
        Returns:
            List of PDF file paths
        """
        pdf_files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            print(f"❌ Directory not found: {directory}")
            return []
        
        # Search for PDF files
        for pdf_file in directory_path.rglob("*.pdf"):
            pdf_files.append(pdf_file)
        
        print(f"📁 Found {len(pdf_files)} PDF files in {directory}")
        return pdf_files
    
    def process_single_file(self, pdf_path: Path, output_dir: Path) -> Dict:
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory for output files
            
        Returns:
            Processing result dictionary
        """
        start_time = time.time()
        
        try:
            print(f"📄 Processing: {pdf_path.name}")
            
            # Load PDF
            if not self.pdf_processor.load_pdf(str(pdf_path)):
                return {"success": False, "error": "Failed to load PDF"}
            
            # Get document info
            doc_info = self.pdf_processor.get_document_info()
            
            # Extract text (with OCR if needed)
            all_text = ""
            page_count = doc_info.get("pages", 0)
            
            for page_num in range(page_count):
                if hasattr(self.pdf_processor, 'extract_text_with_ocr'):
                    page_result = self.pdf_processor.extract_text_with_ocr(page_num)
                    all_text += page_result.get("combined_text", "")
                else:
                    all_text += self.pdf_processor.extract_text_from_page(page_num)
                all_text += "\n\n"
            
            # Analyze content
            content_blocks = self.content_analyzer.analyze_text(all_text)
            
            # Generate markdown
            markdown_content = self.markdown_generator.generate_markdown(content_blocks)
            
            # Add metadata
            title = doc_info.get("title", pdf_path.stem)
            author = doc_info.get("author", "")
            header = self.markdown_generator.add_document_metadata(title, author)
            
            # Generate TOC
            toc = self.markdown_generator.generate_table_of_contents(content_blocks)
            
            # Combine
            final_markdown = header + toc + markdown_content
            
            # Save output
            output_file = output_dir / f"{pdf_path.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
            
            # Clean up
            self.pdf_processor.close_document()
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "input_file": str(pdf_path),
                "output_file": str(output_file),
                "pages": page_count,
                "content_blocks": len(content_blocks),
                "output_size": len(final_markdown),
                "processing_time": processing_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "input_file": str(pdf_path),
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def process_batch(self, input_directory: str, output_directory: str) -> Dict:
        """
        Process all PDF files in a directory.
        
        Args:
            input_directory: Directory containing PDF files
            output_directory: Directory for markdown output
            
        Returns:
            Batch processing summary
        """
        print(f"🚀 Starting batch processing...")
        print(f"   Input: {input_directory}")
        print(f"   Output: {output_directory}")
        
        # Setup directories
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find PDF files
        pdf_files = self.find_pdf_files(input_directory)
        
        if not pdf_files:
            return {"success": False, "error": "No PDF files found"}
        
        # Process each file
        results = []
        start_time = time.time()
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] ", end="")
            
            result = self.process_single_file(pdf_file, output_path)
            results.append(result)
            
            if result["success"]:
                self.processed_files += 1
                print(f"   ✅ Completed in {result['processing_time']:.1f}s")
            else:
                self.failed_files += 1
                print(f"   ❌ Failed: {result['error']}")
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = {
            "total_files": len(pdf_files),
            "processed_successfully": self.processed_files,
            "failed": self.failed_files,
            "total_time": total_time,
            "average_time_per_file": total_time / len(pdf_files),
            "results": results
        }
        
        self._print_summary(summary)
        return summary
    
    def _print_summary(self, summary: Dict):
        """Print batch processing summary."""
        print(f"\n{'='*60}")
        print(f"📊 BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total files: {summary['total_files']}")
        print(f"Successful: {summary['processed_successfully']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {(summary['processed_successfully']/summary['total_files']*100):.1f}%")
        print(f"Total time: {summary['total_time']:.1f} seconds")
        print(f"Average per file: {summary['average_time_per_file']:.1f} seconds")
        
        if summary['failed'] > 0:
            print(f"\n❌ Failed files:")
            for result in summary['results']:
                if not result['success']:
                    print(f"   - {Path(result['input_file']).name}: {result['error']}")
```

## Testing Advanced Features

Create `test_advanced_features.py`:

```python
# test_advanced_features.py
from src.batch_processor import BatchProcessor
from src.ocr_processor import OCRProcessor
import os

def test_ocr():
    """Test OCR functionality."""
    print("🔍 Testing OCR functionality...")
    
    # This would require a PDF with images
    pdf_path = input("Enter path to PDF with images (or press Enter to skip): ")
    
    if pdf_path.strip():
        from src.pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        if processor.load_pdf(pdf_path):
            result = processor.extract_text_with_ocr(0)
            
            print(f"\nDirect text length: {len(result['direct_text'])}")
            print(f"OCR results: {len(result['ocr_results'])}")
            print(f"Combined text length: {len(result['combined_text'])}")
            
            if result['ocr_results']:
                print("\nOCR Results:")
                for i, ocr_result in enumerate(result['ocr_results']):
                    if ocr_result['success']:
                        print(f"  Image {i+1}: {ocr_result['word_count']} words, {ocr_result['confidence']:.1f}% confidence")
    else:
        print("Skipping OCR test")

def test_batch_processing():
    """Test batch processing functionality."""
    print("\n🚀 Testing batch processing...")
    
    input_dir = input("Enter directory with PDF files: ")
    output_dir = input("Enter output directory: ")
    
    if os.path.exists(input_dir):
        processor = BatchProcessor()
        summary = processor.process_batch(input_dir, output_dir)
        
        print(f"\nBatch processing completed!")
        print(f"Check {output_dir} for output files")
    else:
        print("Input directory not found")

if __name__ == "__main__":
    print("🧪 Advanced Features Test Suite")
    print("=" * 40)
    
    test_ocr()
    test_batch_processing()
```

## What We've Accomplished

🎉 **Amazing progress!** Your parser now has enterprise-level features:

- ✅ **OCR Integration**: Can read text from images in PDFs
- ✅ **Intelligent Image Processing**: Detects content types in images
- ✅ **Batch Processing**: Can process multiple PDFs automatically
- ✅ **Performance Monitoring**: Tracks processing time and success rates
- ✅ **Error Handling**: Gracefully handles failures and continues processing
- ✅ **Comprehensive Analysis**: Provides detailed statistics and reports

## Performance Tips

### Optimizing OCR
- Increase image resolution for better accuracy
- Use appropriate OCR configurations for different content types
- Set confidence thresholds to filter out poor results

### Batch Processing
- Process files in smaller batches for large datasets
- Monitor memory usage with large PDFs
- Use parallel processing for even faster results

## What's Next?

In the next guide, we'll focus on testing and quality assurance to ensure your parser works reliably with different types of PDFs and edge cases.

---

[← Previous: Phase 3 - Markdown Generation](06-phase3-markdown-generation.md) | [Next: Testing and Quality Assurance →](08-testing-and-quality-assurance.md)
