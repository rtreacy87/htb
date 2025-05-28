# Testing and Quality Assurance

## Why Testing Matters

Testing ensures your parser works reliably with different types of PDFs and handles edge cases gracefully. Think of testing like quality control in a factory - it catches problems before they reach users!

## Learning Objectives

By the end of this guide, you'll have:
- Comprehensive test suites for all parser components
- Quality metrics and validation systems
- Automated testing workflows
- Error detection and handling strategies

## Types of Testing We'll Implement

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test components working together
3. **Quality Validation**: Measure output quality
4. **Performance Tests**: Ensure acceptable speed
5. **Edge Case Tests**: Handle unusual inputs

## Step 1: Setting Up the Test Framework

Create a `tests` directory structure:

```
tests/
├── __init__.py
├── test_pdf_processor.py
├── test_content_analyzer.py
├── test_markdown_generator.py
├── test_integration.py
├── test_quality.py
└── sample_files/
    ├── simple.pdf
    ├── complex.pdf
    └── image_heavy.pdf
```

First, create `tests/__init__.py` (empty file) and then our test utilities:

```python
# tests/test_utils.py
import os
import tempfile
from pathlib import Path
from typing import Dict, List

class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def create_temp_file(content: str, suffix: str = ".txt") -> str:
        """Create a temporary file with given content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            return f.name
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """Remove a temporary file."""
        try:
            os.unlink(file_path)
        except FileNotFoundError:
            pass
    
    @staticmethod
    def get_sample_text() -> str:
        """Get sample text for testing."""
        return """
# HTB Machine: Example

## Reconnaissance

nmap -sV 10.10.10.1
Starting Nmap 7.80 scan...

The target machine is running:
- SSH on port 22
- HTTP on port 80

## Exploitation

Let's check the web service:

gobuster dir -u http://10.10.10.1 -w /usr/share/wordlists/common.txt

Found interesting directory: /admin

def exploit_function():
    payload = "test"
    return payload
"""
    
    @staticmethod
    def assert_markdown_quality(markdown: str) -> Dict:
        """Check markdown quality and return metrics."""
        lines = markdown.split('\n')
        
        metrics = {
            "has_headings": any(line.startswith('#') for line in lines),
            "has_code_blocks": '```' in markdown,
            "has_inline_code": '`' in markdown and '```' not in markdown.replace('```', ''),
            "line_count": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
        return metrics
```

## Step 2: Unit Tests for PDF Processor

Create `tests/test_pdf_processor.py`:

```python
# tests/test_pdf_processor.py
import pytest
import tempfile
from pathlib import Path
from src.pdf_processor import PDFProcessor

class TestPDFProcessor:
    """Test cases for PDF processor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()
    
    def teardown_method(self):
        """Clean up after tests."""
        if self.processor.current_document:
            self.processor.close_document()
    
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        result = self.processor.load_pdf("nonexistent.pdf")
        assert result == False
    
    def test_load_invalid_file(self):
        """Test loading a non-PDF file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not a PDF")
            temp_path = f.name
        
        try:
            result = self.processor.load_pdf(temp_path)
            assert result == False
        finally:
            Path(temp_path).unlink()
    
    def test_extract_without_loaded_document(self):
        """Test extracting text without loading a document first."""
        result = self.processor.extract_text_from_page(0)
        assert "Error: No document loaded" in result
    
    def test_get_info_without_document(self):
        """Test getting document info without loading a document."""
        info = self.processor.get_document_info()
        assert "error" in info
    
    def test_extract_invalid_page(self):
        """Test extracting from a page that doesn't exist."""
        # This test requires a valid PDF file
        # For now, we'll test the error handling logic
        if self.processor.current_document is None:
            result = self.processor.extract_text_from_page(999)
            assert "Error: No document loaded" in result

# Run with: python -m pytest tests/test_pdf_processor.py -v
```

## Step 3: Unit Tests for Content Analyzer

Create `tests/test_content_analyzer.py`:

```python
# tests/test_content_analyzer.py
import pytest
from src.content_analyzer import ContentAnalyzer, ContentBlock

class TestContentAnalyzer:
    """Test cases for content analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ContentAnalyzer()
    
    def test_classify_command(self):
        """Test command classification."""
        test_cases = [
            "nmap -sV 10.10.10.1",
            "gobuster dir -u http://example.com",
            "python3 script.py",
            "sudo apt update"
        ]
        
        for command in test_cases:
            result = self.analyzer.classify_line(command)
            assert result.content_type == "command"
            assert result.confidence > 0.8
    
    def test_classify_heading(self):
        """Test heading classification."""
        test_cases = [
            "# Reconnaissance",
            "EXPLOITATION",
            "1. Initial Enumeration",
            "Privilege Escalation"
        ]
        
        for heading in test_cases:
            result = self.analyzer.classify_line(heading)
            assert result.content_type == "heading"
    
    def test_classify_code(self):
        """Test code classification."""
        test_cases = [
            "def exploit_function():",
            "function getData() {",
            "import requests",
            "<?php echo 'hello'; ?>"
        ]
        
        for code in test_cases:
            result = self.analyzer.classify_line(code)
            assert result.content_type == "code"
    
    def test_classify_network(self):
        """Test network content classification."""
        test_cases = [
            "10.10.10.1",
            "192.168.1.100:8080",
            "The target IP is 172.16.0.1"
        ]
        
        for network in test_cases:
            result = self.analyzer.classify_line(network)
            assert result.content_type == "network"
    
    def test_classify_path(self):
        """Test file path classification."""
        test_cases = [
            "/etc/passwd",
            "C:\\Windows\\System32",
            "~/Documents/file.txt"
        ]
        
        for path in test_cases:
            result = self.analyzer.classify_line(path)
            assert result.content_type == "path"
    
    def test_classify_url(self):
        """Test URL classification."""
        test_cases = [
            "http://example.com",
            "https://10.10.10.1/admin",
            "ftp://files.example.com"
        ]
        
        for url in test_cases:
            result = self.analyzer.classify_line(url)
            assert result.content_type == "url"
    
    def test_classify_empty_line(self):
        """Test empty line classification."""
        result = self.analyzer.classify_line("")
        assert result.content_type == "empty"
        assert result.confidence == 1.0
    
    def test_analyze_multiline_text(self):
        """Test analyzing multiple lines of text."""
        text = """# Reconnaissance
nmap -sV 10.10.10.1
The target is running SSH on port 22."""
        
        blocks = self.analyzer.analyze_text(text)
        
        assert len(blocks) == 3
        assert blocks[0].content_type == "heading"
        assert blocks[1].content_type == "command"
        assert blocks[2].content_type == "network"
    
    def test_statistics_generation(self):
        """Test statistics generation."""
        blocks = [
            ContentBlock("# Test", "heading", 0.9),
            ContentBlock("nmap -sV", "command", 0.95),
            ContentBlock("Some text", "text", 0.8)
        ]
        
        stats = self.analyzer.get_statistics(blocks)
        
        assert stats["total_blocks"] == 3
        assert "heading" in stats["content_types"]
        assert "command" in stats["content_types"]
        assert "text" in stats["content_types"]
        assert stats["confidence_avg"] > 0.8

# Run with: python -m pytest tests/test_content_analyzer.py -v
```

## Step 4: Quality Validation Tests

Create `tests/test_quality.py`:

```python
# tests/test_quality.py
import pytest
from src.content_analyzer import ContentAnalyzer
from src.markdown_generator import MarkdownGenerator
from tests.test_utils import TestUtils

class TestQuality:
    """Test cases for output quality validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ContentAnalyzer()
        self.generator = MarkdownGenerator()
        self.utils = TestUtils()
    
    def test_markdown_structure_quality(self):
        """Test that generated markdown has proper structure."""
        sample_text = self.utils.get_sample_text()
        
        # Analyze content
        blocks = self.analyzer.analyze_text(sample_text)
        
        # Generate markdown
        markdown = self.generator.generate_markdown(blocks)
        
        # Check quality metrics
        metrics = self.utils.assert_markdown_quality(markdown)
        
        assert metrics["has_headings"], "Markdown should contain headings"
        assert metrics["has_code_blocks"], "Markdown should contain code blocks"
        assert metrics["non_empty_lines"] > 0, "Markdown should have content"
    
    def test_command_formatting_quality(self):
        """Test that commands are properly formatted."""
        commands = [
            "nmap -sV 10.10.10.1",
            "gobuster dir -u http://example.com -w wordlist.txt",
            "python3 exploit.py"
        ]
        
        for command in commands:
            block = self.analyzer.classify_line(command)
            markdown = self.generator._format_block(block)
            
            # Should be in code block or inline code
            assert "```" in markdown or "`" in markdown, f"Command should be formatted: {command}"
    
    def test_heading_hierarchy(self):
        """Test that headings maintain proper hierarchy."""
        headings = [
            "# Main Section",
            "## Subsection", 
            "### Sub-subsection"
        ]
        
        markdown_lines = []
        for heading in headings:
            block = self.analyzer.classify_line(heading)
            formatted = self.generator._format_block(block)
            markdown_lines.append(formatted)
        
        # Check hierarchy
        assert markdown_lines[0].startswith("#")
        assert markdown_lines[1].startswith("##")
        assert markdown_lines[2].startswith("###")
    
    def test_content_preservation(self):
        """Test that important content is preserved."""
        important_content = [
            "10.10.10.1",  # IP address
            "/etc/passwd",  # File path
            "http://example.com",  # URL
            "nmap -sV"  # Command
        ]
        
        sample_text = "\n".join(important_content)
        blocks = self.analyzer.analyze_text(sample_text)
        markdown = self.generator.generate_markdown(blocks)
        
        # All important content should be preserved
        for content in important_content:
            assert content in markdown, f"Content should be preserved: {content}"
    
    def test_confidence_thresholds(self):
        """Test that classification confidence meets thresholds."""
        test_cases = [
            ("nmap -sV 10.10.10.1", "command", 0.85),
            ("# Reconnaissance", "heading", 0.75),
            ("def function():", "code", 0.80),
            ("192.168.1.1", "network", 0.85)
        ]
        
        for text, expected_type, min_confidence in test_cases:
            block = self.analyzer.classify_line(text)
            
            assert block.content_type == expected_type
            assert block.confidence >= min_confidence, f"Low confidence for {text}: {block.confidence}"

# Run with: python -m pytest tests/test_quality.py -v
```

## Step 5: Integration Tests

Create `tests/test_integration.py`:

```python
# tests/test_integration.py
import pytest
import tempfile
from pathlib import Path
from src.pdf_processor import PDFProcessor
from src.content_analyzer import ContentAnalyzer
from src.markdown_generator import MarkdownGenerator

class TestIntegration:
    """Integration tests for the complete parser pipeline."""
    
    def setup_method(self):
        """Set up test components."""
        self.pdf_processor = PDFProcessor()
        self.content_analyzer = ContentAnalyzer()
        self.markdown_generator = MarkdownGenerator()
    
    def test_complete_pipeline_with_sample_text(self):
        """Test the complete pipeline with sample text."""
        # Sample text that represents extracted PDF content
        sample_text = """
# HTB Machine: TestBox

## Reconnaissance

nmap -sV 10.10.10.1
Starting Nmap scan...

## Exploitation

The target is vulnerable to:
- SQL injection on /login.php
- Directory traversal in /files/

gobuster dir -u http://10.10.10.1 -w /usr/share/wordlists/common.txt

def exploit():
    payload = "' OR 1=1--"
    return payload
"""
        
        # Analyze content
        blocks = self.content_analyzer.analyze_text(sample_text)
        
        # Verify we have different content types
        content_types = {block.content_type for block in blocks if block.text.strip()}
        assert "heading" in content_types
        assert "command" in content_types
        assert "text" in content_types
        
        # Generate markdown
        markdown = self.markdown_generator.generate_markdown(blocks)
        
        # Verify markdown quality
        assert "# HTB Machine: TestBox" in markdown
        assert "```" in markdown  # Should have code blocks
        assert "nmap" in markdown  # Commands should be preserved
        
        # Verify structure
        lines = markdown.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) > 5  # Should have substantial content
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Test with problematic input
        problematic_text = "\x00\x01\x02Invalid characters"
        
        try:
            blocks = self.content_analyzer.analyze_text(problematic_text)
            markdown = self.markdown_generator.generate_markdown(blocks)
            
            # Should handle gracefully without crashing
            assert isinstance(markdown, str)
            
        except Exception as e:
            pytest.fail(f"Pipeline should handle problematic input gracefully: {e}")
    
    def test_performance_with_large_content(self):
        """Test performance with larger content."""
        import time
        
        # Generate large sample text
        large_text = """
# Large Document Test

## Section 1
""" + "\n".join([f"Line {i}: nmap -sV 192.168.1.{i%255}" for i in range(100)])
        
        start_time = time.time()
        
        # Process large content
        blocks = self.content_analyzer.analyze_text(large_text)
        markdown = self.markdown_generator.generate_markdown(blocks)
        
        processing_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 5.0, f"Processing took too long: {processing_time:.2f}s"
        assert len(blocks) > 50  # Should have processed many blocks
        assert len(markdown) > 1000  # Should have generated substantial output

# Run with: python -m pytest tests/test_integration.py -v
```

## Step 6: Running All Tests

Create a test runner script `run_tests.py`:

```python
# run_tests.py
import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all test suites and generate a report."""
    
    print("🧪 HTB Parser Test Suite")
    print("=" * 50)
    
    test_files = [
        "tests/test_pdf_processor.py",
        "tests/test_content_analyzer.py", 
        "tests/test_quality.py",
        "tests/test_integration.py"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n📋 Running {test_file}...")
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_file, "-v"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - All tests passed")
                    # Count passed tests (rough estimate)
                    passed = result.stdout.count("PASSED")
                    total_passed += passed
                else:
                    print(f"❌ {test_file} - Some tests failed")
                    failed = result.stdout.count("FAILED")
                    total_failed += failed
                    print(result.stdout)
                    
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                total_failed += 1
        else:
            print(f"⚠️ Test file not found: {test_file}")
    
    print(f"\n{'='*50}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total passed: {total_passed}")
    print(f"Total failed: {total_failed}")
    
    if total_failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
```

## Quality Metrics and Validation

### Key Quality Indicators

1. **Classification Accuracy**: >90% for common content types
2. **Content Preservation**: 100% of important content retained
3. **Markdown Validity**: All output should be valid markdown
4. **Processing Speed**: <30 seconds per typical writeup
5. **Error Rate**: <5% failure rate on valid PDFs

### Automated Quality Checks

Create `quality_checker.py`:

```python
# quality_checker.py
def check_markdown_quality(markdown: str) -> dict:
    """Comprehensive markdown quality check."""
    
    issues = []
    warnings = []
    
    # Check for basic structure
    if not markdown.strip():
        issues.append("Empty output")
    
    if "```" not in markdown:
        warnings.append("No code blocks found")
    
    if not any(line.startswith('#') for line in markdown.split('\n')):
        warnings.append("No headings found")
    
    # Check for common formatting issues
    lines = markdown.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('```') and not line.strip().endswith('```'):
            # Check if code block is properly closed
            remaining_lines = lines[i+1:]
            if not any('```' in remaining_line for remaining_line in remaining_lines):
                issues.append(f"Unclosed code block at line {i+1}")
    
    return {
        "issues": issues,
        "warnings": warnings,
        "quality_score": max(0, 100 - len(issues)*20 - len(warnings)*5)
    }
```

## What We've Accomplished

🎉 **Excellent work!** You now have a comprehensive testing framework:

- ✅ **Unit Tests**: Test individual components thoroughly
- ✅ **Integration Tests**: Verify components work together
- ✅ **Quality Validation**: Ensure output meets standards
- ✅ **Performance Tests**: Monitor processing speed
- ✅ **Error Handling**: Graceful failure management
- ✅ **Automated Testing**: Easy-to-run test suites

## Best Practices for Testing

1. **Test Early and Often**: Run tests after each change
2. **Cover Edge Cases**: Test with unusual inputs
3. **Monitor Performance**: Track processing times
4. **Validate Output**: Check markdown quality automatically
5. **Document Issues**: Keep track of known problems

## What's Next?

In the next guide, we'll cover troubleshooting common issues and how to debug problems when they arise.

---

[← Previous: Phase 4 - Advanced Features](07-phase4-advanced-features.md) | [Next: Troubleshooting Guide →](09-troubleshooting-guide.md)
