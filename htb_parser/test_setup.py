import sys
print(f"Python version: {sys.version}")

try:
    import fitz  # PyMuPDF
    print("✅ PyMuPDF installed successfully")
except ImportError:
    print("❌ PyMuPDF not found")

try:
    import pdfplumber
    print("✅ pdfplumber installed successfully")
except ImportError:
    print("❌ pdfplumber not found")

try:
    import pytesseract
    print("✅ pytesseract installed successfully")
except ImportError:
    print("❌ pytesseract not found")

print("🎉 Setup test complete!")
