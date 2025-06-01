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


