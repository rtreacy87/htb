# Troubleshooting Guide

## Common Issues and Solutions

This guide helps you diagnose and fix common problems you might encounter while building and using the HTB parser. Think of it as your debugging toolkit!

## General Debugging Strategy

When something goes wrong:

1. **Read the error message carefully** - It often tells you exactly what's wrong
2. **Check the basics first** - File paths, permissions, dependencies
3. **Isolate the problem** - Test components individually
4. **Use print statements** - Add debug output to see what's happening
5. **Check your inputs** - Verify PDF files are valid and accessible

## Installation and Setup Issues

### Issue: "Python not found" or "Command not found"

**Symptoms:**
```bash
python: command not found
# or
'python' is not recognized as an internal or external command
```

**Solutions:**
1. **Check Python installation:**
   ```bash
   python --version
   python3 --version
   ```

2. **Add Python to PATH (Windows):**
   - Reinstall Python with "Add to PATH" checked
   - Or manually add Python directory to system PATH

3. **Use python3 instead of python (Mac/Linux):**
   ```bash
   python3 your_script.py
   ```

### Issue: "Module not found" errors

**Symptoms:**
```python
ModuleNotFoundError: No module named 'fitz'
ImportError: No module named 'src.pdf_processor'
```

**Solutions:**
1. **Check virtual environment is active:**
   ```bash
   # Should see (venv) in prompt
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Reinstall requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python path for local imports:**
   ```python
   import sys
   sys.path.append('.')  # Add current directory to path
   ```

### Issue: "Permission denied" errors

**Symptoms:**
```bash
PermissionError: [Errno 13] Permission denied: 'file.pdf'
```

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la file.pdf  # Mac/Linux
   ```

2. **Run with appropriate permissions:**
   ```bash
   sudo python script.py  # Use carefully!
   ```

3. **Move files to accessible location:**
   - Copy PDFs to your project directory
   - Avoid system directories

## PDF Processing Issues

### Issue: "Failed to load PDF" or "Invalid PDF"

**Symptoms:**
```
❌ Error loading PDF: [Errno 2] No such file or directory
❌ Error loading PDF: cannot open broken document
```

**Debugging Steps:**
1. **Verify file exists and path is correct:**
   ```python
   from pathlib import Path
   pdf_path = "your_file.pdf"
   print(f"File exists: {Path(pdf_path).exists()}")
   print(f"Full path: {Path(pdf_path).absolute()}")
   ```

2. **Check file is actually a PDF:**
   ```bash
   file your_file.pdf  # Should show "PDF document"
   ```

3. **Test with a simple PDF:**
   - Try with a basic PDF first
   - Gradually test more complex files

4. **Check PDF isn't password protected:**
   ```python
   import fitz
   doc = fitz.open("file.pdf")
   print(f"Needs password: {doc.needs_pass}")
   ```

### Issue: "No text extracted" or "Empty output"

**Symptoms:**
- PDF loads successfully but no text is extracted
- Output file is empty or contains only page markers

**Debugging Steps:**
1. **Check if PDF contains text or just images:**
   ```python
   # Add to your PDF processor
   def debug_page_content(self, page_number):
       page = self.current_document[page_number]
       text_dict = page.get_text("dict")
       
       print(f"Text blocks: {len(text_dict.get('blocks', []))}")
       print(f"Images: {len(page.get_images())}")
       
       # Show first few characters
       text = page.get_text()
       print(f"Sample text: {text[:100]}...")
   ```

2. **Enable OCR for image-heavy PDFs:**
   ```python
   processor.use_ocr = True
   result = processor.extract_text_with_ocr(page_number)
   ```

3. **Try different extraction methods:**
   ```python
   # Try different text extraction modes
   text1 = page.get_text()           # Default
   text2 = page.get_text("text")     # Plain text
   text3 = page.get_text("blocks")   # Block structure
   ```

## Content Analysis Issues

### Issue: "Poor classification accuracy"

**Symptoms:**
- Commands classified as regular text
- Headings not recognized
- Low confidence scores

**Debugging Steps:**
1. **Test individual classifications:**
   ```python
   analyzer = ContentAnalyzer()
   
   test_lines = [
       "nmap -sV 10.10.10.1",
       "# Reconnaissance", 
       "def exploit():"
   ]
   
   for line in test_lines:
       result = analyzer.classify_line(line)
       print(f"'{line}' -> {result.content_type} ({result.confidence:.2f})")
   ```

2. **Check pattern matching:**
   ```python
   import re
   
   # Test specific patterns
   command_pattern = r'^[a-zA-Z0-9_\-\.]+\s+\-[a-zA-Z0-9\-]+'
   test_text = "nmap -sV 10.10.10.1"
   
   if re.match(command_pattern, test_text):
       print("Pattern matches!")
   else:
       print("Pattern doesn't match")
   ```

3. **Adjust confidence thresholds:**
   ```python
   # Lower thresholds for testing
   self.confidence_threshold = 50  # Instead of 60
   ```

### Issue: "Content misclassification"

**Common Problems and Fixes:**

1. **Commands in explanatory text:**
   ```python
   # Problem: "The nmap command scans ports"
   # Solution: Require commands to start at line beginning
   pattern = r'^(nmap|gobuster|dirb)'  # Add ^ anchor
   ```

2. **IP addresses in file paths:**
   ```python
   # Problem: "/var/log/192.168.1.1.log" classified as network
   # Solution: Check context
   def _check_network(self, line):
       if line.startswith('/') or line.startswith('C:\\'):
           return None  # Likely a file path
       # ... rest of network checking
   ```

3. **False heading detection:**
   ```python
   # Problem: Long sentences classified as headings
   # Solution: Add length limits
   if len(line) > 100:  # Too long for heading
       return None
   ```

## Markdown Generation Issues

### Issue: "Malformed markdown output"

**Symptoms:**
- Unclosed code blocks
- Broken formatting
- Invalid markdown syntax

**Debugging Steps:**
1. **Validate markdown syntax:**
   ```python
   def validate_markdown(markdown):
       lines = markdown.split('\n')
       code_block_count = 0
       
       for i, line in enumerate(lines):
           if line.strip().startswith('```'):
               code_block_count += 1
       
       if code_block_count % 2 != 0:
           print("⚠️ Unmatched code blocks!")
       
       return code_block_count % 2 == 0
   ```

2. **Check code block pairing:**
   ```python
   def debug_code_blocks(markdown):
       lines = markdown.split('\n')
       in_code_block = False
       
       for i, line in enumerate(lines):
           if line.strip().startswith('```'):
               in_code_block = not in_code_block
               print(f"Line {i+1}: Code block {'opened' if in_code_block else 'closed'}")
   ```

### Issue: "Poor formatting quality"

**Solutions:**
1. **Add spacing rules:**
   ```python
   def _needs_spacing(self, previous_type, current_type):
       # Always space before headings
       if current_type == "heading":
           return True
       
       # Space between different content types
       if previous_type != current_type:
           return True
       
       return False
   ```

2. **Improve language detection:**
   ```python
   def _detect_command_language(self, command):
       command_lower = command.lower()
       
       # More specific patterns
       if any(tool in command_lower for tool in ["nmap", "gobuster", "curl"]):
           return "bash"
       elif command_lower.startswith("python"):
           return "python"
       elif "select" in command_lower or "insert" in command_lower:
           return "sql"
       
       return "bash"  # Default
   ```

## OCR Issues

### Issue: "OCR not working" or "Poor OCR accuracy"

**Symptoms:**
```
❌ OCR failed: [Errno 2] No such file or directory: 'tesseract'
⚠️ Low OCR confidence scores
```

**Solutions:**
1. **Check Tesseract installation:**
   ```bash
   tesseract --version
   # Should show version info
   ```

2. **Install Tesseract if missing:**
   ```bash
   # Mac
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt install tesseract-ocr
   
   # Windows: Download from GitHub releases
   ```

3. **Improve OCR accuracy:**
   ```python
   # Preprocess images for better OCR
   def preprocess_image(image):
       # Convert to grayscale
       image = image.convert('L')
       
       # Increase size if too small
       width, height = image.size
       if width < 300:
           scale = 300 / width
           new_size = (int(width * scale), int(height * scale))
           image = image.resize(new_size, Image.Resampling.LANCZOS)
       
       return image
   ```

4. **Adjust OCR configuration:**
   ```python
   # Try different OCR modes
   configs = [
       "--oem 3 --psm 6",  # Default
       "--oem 3 --psm 4",  # Single column
       "--oem 3 --psm 8",  # Single word
   ]
   ```

## Performance Issues

### Issue: "Slow processing" or "High memory usage"

**Symptoms:**
- Processing takes very long
- System becomes unresponsive
- Memory usage keeps growing

**Solutions:**
1. **Process pages individually:**
   ```python
   # Instead of loading all text at once
   for page_num in range(doc_pages):
       page_text = processor.extract_text_from_page(page_num)
       # Process immediately
       blocks = analyzer.analyze_text(page_text)
       # Clear memory
       del page_text
   ```

2. **Limit OCR processing:**
   ```python
   # Skip OCR for pages with sufficient text
   def should_use_ocr(self, page_text):
       return len(page_text.strip()) < 100  # Only OCR if little text
   ```

3. **Monitor memory usage:**
   ```python
   import psutil
   import os
   
   def check_memory():
       process = psutil.Process(os.getpid())
       memory_mb = process.memory_info().rss / 1024 / 1024
       print(f"Memory usage: {memory_mb:.1f} MB")
   ```

## Debugging Tools and Techniques

### Add Debug Logging

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in your code
logger.debug(f"Processing page {page_num}")
logger.info(f"Extracted {len(text)} characters")
logger.warning(f"Low confidence: {confidence}")
logger.error(f"Failed to process: {error}")
```

### Create Debug Output

```python
def debug_content_analysis(text, output_file="debug_analysis.txt"):
    """Create detailed debug output for content analysis."""
    
    analyzer = ContentAnalyzer()
    blocks = analyzer.analyze_text(text)
    
    with open(output_file, 'w') as f:
        f.write("CONTENT ANALYSIS DEBUG\n")
        f.write("=" * 50 + "\n\n")
        
        for i, block in enumerate(blocks):
            f.write(f"Block {i+1}:\n")
            f.write(f"  Text: {repr(block.text)}\n")
            f.write(f"  Type: {block.content_type}\n")
            f.write(f"  Confidence: {block.confidence:.2f}\n")
            f.write(f"  Metadata: {block.metadata}\n")
            f.write("-" * 30 + "\n")
    
    print(f"Debug output saved to {output_file}")
```

### Test with Minimal Examples

```python
def test_minimal_example():
    """Test with the simplest possible input."""
    
    # Start with one line
    simple_text = "nmap -sV 10.10.10.1"
    
    analyzer = ContentAnalyzer()
    result = analyzer.classify_line(simple_text)
    
    print(f"Input: {simple_text}")
    print(f"Type: {result.content_type}")
    print(f"Confidence: {result.confidence}")
    
    # If this works, gradually add complexity
```

## Getting Help

### When to Ask for Help

- You've tried the solutions above
- Error messages are unclear
- Problem persists across different files
- Performance is unacceptably slow

### How to Report Issues

When asking for help, include:

1. **Exact error message**
2. **Steps to reproduce**
3. **Your environment** (OS, Python version)
4. **Sample input** (if possible)
5. **What you've already tried**

### Useful Commands for Diagnostics

```bash
# Check Python environment
python --version
pip list

# Check file details
file your_file.pdf
ls -la your_file.pdf

# Test individual components
python -c "import fitz; print('PyMuPDF OK')"
python -c "import pytesseract; print('Tesseract OK')"

# Run with verbose output
python your_script.py -v
```

## Prevention Tips

1. **Start simple** - Test with basic PDFs first
2. **Validate inputs** - Check files before processing
3. **Use version control** - Save working versions
4. **Test incrementally** - Add features one at a time
5. **Monitor resources** - Watch memory and CPU usage

Remember: Every expert was once a beginner who encountered these same issues. Debugging is a skill that improves with practice!

---

[← Previous: Testing and Quality Assurance](08-testing-and-quality-assurance.md) | [Next: Next Steps and Extensions →](10-next-steps-and-extensions.md)
