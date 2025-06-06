#!/usr/bin/env python3
"""
Simple test to verify all imports work correctly.
"""

def test_all_imports():
    """Test that all modules can be imported successfully."""
    
    print("Testing imports...")
    
    try:
        from src.pdf_processor import PDFProcessor
        print("✅ PDFProcessor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PDFProcessor: {e}")
        return False
    
    try:
        from src.content_analyzer import ContentAnalyzer, ContentBlock
        print("✅ ContentAnalyzer and ContentBlock imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ContentAnalyzer/ContentBlock: {e}")
        return False
    
    try:
        from src.markdown_generator import MarkdownGenerator
        print("✅ MarkdownGenerator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MarkdownGenerator: {e}")
        return False
    
    # Test that we can create instances
    try:
        pdf_processor = PDFProcessor()
        content_analyzer = ContentAnalyzer()
        markdown_generator = MarkdownGenerator()
        print("✅ All instances created successfully")
    except Exception as e:
        print(f"❌ Failed to create instances: {e}")
        return False
    
    # Test basic functionality
    try:
        # Test content analysis
        test_text = "# Test Heading\nnmap -sV 10.10.10.1\nThis is regular text."
        blocks = content_analyzer.analyze_text(test_text)
        print(f"✅ Content analysis works: {len(blocks)} blocks created")
        
        # Test markdown generation
        markdown = markdown_generator.generate_markdown(blocks)
        print(f"✅ Markdown generation works: {len(markdown)} characters generated")
        
    except Exception as e:
        print(f"❌ Failed basic functionality test: {e}")
        return False
    
    print("\n🎉 All imports and basic functionality tests passed!")
    return True

if __name__ == "__main__":
    test_all_imports()
