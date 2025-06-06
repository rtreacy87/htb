# complete_parser_test.py
from src.pdf_processor import PDFProcessor
from src.content_analyzer import ContentAnalyzer
from src.markdown_generator import MarkdownGenerator

def complete_pdf_to_markdown():
    """Complete test of PDF to Markdown conversion."""
    
    # Initialize all components
    pdf_processor = PDFProcessor()
    content_analyzer = ContentAnalyzer()
    markdown_generator = MarkdownGenerator()
    
    # Get input from user
    pdf_path = input("Enter PDF file path: ")
    output_path = input("Enter output markdown file path (e.g., output.md): ")
    
    if pdf_processor.load_pdf(pdf_path):
        print("📄 Processing PDF...")
        
        # Get document info for metadata
        doc_info = pdf_processor.get_document_info()
        
        # Extract all text
        all_text = pdf_processor.extract_all_text()
        
        print("🔍 Analyzing content...")
        
        # Analyze content
        content_blocks = content_analyzer.analyze_text(all_text)
        
        print("📝 Generating markdown...")
        
        # Generate markdown
        markdown_content = markdown_generator.generate_markdown(content_blocks)
        
        # Add document header
        title = doc_info.get("title", "HTB Writeup")
        author = doc_info.get("author", "")
        header = markdown_generator.add_document_metadata(title, author)
        
        # Generate table of contents
        toc = markdown_generator.generate_table_of_contents(content_blocks)
        
        # Combine everything
        final_markdown = header + toc + markdown_content
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)
        
        print(f"✅ Markdown saved to {output_path}")
        
        # Show statistics
        stats = content_analyzer.get_statistics(content_blocks)
        print(f"\n📊 Conversion Statistics:")
        print(f"Total content blocks: {stats['total_blocks']}")
        print(f"Average confidence: {stats['confidence_avg']:.2f}")
        print(f"Output file size: {len(final_markdown)} characters")
        
        print(f"\nContent breakdown:")
        for content_type, count in stats['content_types'].items():
            percentage = (count / stats['total_blocks']) * 100
            print(f"  {content_type:10s}: {count:3d} ({percentage:5.1f}%)")
        
        pdf_processor.close_document()
        
        # Ask if user wants to preview
        preview = input("\nWould you like to preview the first 20 lines? [y/n]: ")
        if preview.lower() == 'y':
            lines = final_markdown.split('\n')[:20]
            print("\n" + "="*60)
            print("MARKDOWN PREVIEW:")
            print("="*60)
            for line in lines:
                print(line)
            print("="*60)

if __name__ == "__main__":
    complete_pdf_to_markdown()

