# Phase 2: Content Recognition and Classification

## What We're Building in This Phase

Now that we can extract text from PDFs, we need to make our parser "smart" - able to recognize different types of content and understand what each piece of text represents.

## Learning Objectives

By the end of this phase, you'll have:
- A content analyzer that can identify different text types
- Pattern recognition for commands, code, and technical content
- A classification system for HTB-specific elements
- Better structure detection for proper markdown conversion

## Understanding Content Classification

### Why Do We Need This?

Raw extracted text looks like this:
```
Reconnaissance
nmap -sV 10.10.10.1
The target machine is running SSH on port 22
```

But we need to know:
- "Reconnaissance" is a heading
- "nmap -sV 10.10.10.1" is a command
- "The target machine..." is explanatory text

### Types of Content We'll Identify

1. **Headings**: Section titles and subsections
2. **Commands**: Terminal commands and tool usage
3. **Code**: Programming code in various languages
4. **IP Addresses**: Network addresses and ports
5. **File Paths**: System paths and directories
6. **URLs**: Web addresses and links
7. **Regular Text**: Explanations and descriptions

## Step 1: Create the Content Analyzer

Create a new file `src/content_analyzer.py`:

```python
# src/content_analyzer.py
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ContentBlock:
    """Represents a classified block of content."""
    text: str
    content_type: str
    confidence: float
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ContentAnalyzer:
    """
    Analyzes extracted text and classifies different content types.
    
    This is like a smart librarian that can look at text and 
    immediately know what category it belongs to.
    """
    
    def __init__(self):
        """Initialize the content analyzer with pattern definitions."""
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Define regex patterns for different content types."""
        
        # Command patterns - common HTB tools and syntax
        self.command_patterns = [
            r'^[a-zA-Z0-9_\-\.]+\s+\-[a-zA-Z0-9\-]+',  # tool with flags
            r'^(nmap|gobuster|dirb|nikto|sqlmap|hydra|john|hashcat)',  # common tools
            r'^(sudo|su|cd|ls|cat|grep|find|chmod|chown)',  # basic commands
            r'^(python|python3|php|bash|sh|perl|ruby)',  # script execution
            r'^\$\s+',  # shell prompt
            r'^#\s+',   # root prompt
        ]
        
        # Code patterns - programming languages
        self.code_patterns = [
            r'def\s+\w+\s*\(',  # Python function
            r'function\s+\w+\s*\(',  # JavaScript function
            r'public\s+class\s+\w+',  # Java class
            r'<\?php',  # PHP opening tag
            r'#!/bin/(bash|sh|python)',  # Shebang
            r'import\s+\w+',  # Import statements
            r'from\s+\w+\s+import',  # Python imports
        ]
        
        # Network patterns
        self.network_patterns = [
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',  # IP addresses
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+\b',  # IP:port
            r'\b[a-fA-F0-9]{1,4}(?::[a-fA-F0-9]{1,4}){7}\b',  # IPv6
        ]
        
        # File path patterns
        self.path_patterns = [
            r'/[a-zA-Z0-9_\-\./]+',  # Unix paths
            r'[A-Za-z]:\\[a-zA-Z0-9_\-\\\./]+',  # Windows paths
            r'~/[a-zA-Z0-9_\-\./]*',  # Home directory paths
        ]
        
        # URL patterns
        self.url_patterns = [
            r'https?://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+',
            r'ftp://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+',
        ]
        
        # Heading patterns
        self.heading_patterns = [
            r'^[A-Z][A-Za-z\s]+$',  # Title case
            r'^[0-9]+\.\s+[A-Z]',  # Numbered sections
            r'^[A-Z\s]+$',  # ALL CAPS
        ]
    
    def classify_line(self, line: str) -> ContentBlock:
        """
        Classify a single line of text.
        
        Args:
            line: Text line to classify
            
        Returns:
            ContentBlock with classification results
        """
        line = line.strip()
        
        if not line:
            return ContentBlock(line, "empty", 1.0)
        
        # Check for commands first (highest priority)
        command_result = self._check_command(line)
        if command_result:
            return command_result
        
        # Check for code
        code_result = self._check_code(line)
        if code_result:
            return code_result
        
        # Check for headings
        heading_result = self._check_heading(line)
        if heading_result:
            return heading_result
        
        # Check for network elements
        network_result = self._check_network(line)
        if network_result:
            return network_result
        
        # Check for file paths
        path_result = self._check_path(line)
        if path_result:
            return path_result
        
        # Check for URLs
        url_result = self._check_url(line)
        if url_result:
            return url_result
        
        # Default to regular text
        return ContentBlock(line, "text", 0.8)
    
    def _check_command(self, line: str) -> Optional[ContentBlock]:
        """Check if line is a command."""
        for pattern in self.command_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                # Determine shell type
                shell_type = "bash"
                if line.startswith("python"):
                    shell_type = "python"
                elif line.startswith("php"):
                    shell_type = "php"
                
                return ContentBlock(
                    line, 
                    "command", 
                    0.9,
                    {"shell_type": shell_type}
                )
        return None
    
    def _check_code(self, line: str) -> Optional[ContentBlock]:
        """Check if line is code."""
        for pattern in self.code_patterns:
            if re.search(pattern, line):
                # Determine language
                language = "unknown"
                if "def " in line:
                    language = "python"
                elif "function " in line:
                    language = "javascript"
                elif "<?php" in line:
                    language = "php"
                elif "public class" in line:
                    language = "java"
                
                return ContentBlock(
                    line, 
                    "code", 
                    0.85,
                    {"language": language}
                )
        return None
    
    def _check_heading(self, line: str) -> Optional[ContentBlock]:
        """Check if line is a heading."""
        # Skip very long lines (unlikely to be headings)
        if len(line) > 100:
            return None
        
        for pattern in self.heading_patterns:
            if re.match(pattern, line):
                # Determine heading level based on characteristics
                level = 1
                if re.match(r'^[0-9]+\.', line):
                    level = 2  # Numbered sections are usually H2
                elif line.isupper() and len(line) < 30:
                    level = 1  # Short ALL CAPS are usually H1
                else:
                    level = 2  # Default to H2
                
                return ContentBlock(
                    line, 
                    "heading", 
                    0.8,
                    {"level": level}
                )
        return None
    
    def _check_network(self, line: str) -> Optional[ContentBlock]:
        """Check if line contains network information."""
        for pattern in self.network_patterns:
            if re.search(pattern, line):
                return ContentBlock(
                    line, 
                    "network", 
                    0.9,
                    {"contains_ip": True}
                )
        return None
    
    def _check_path(self, line: str) -> Optional[ContentBlock]:
        """Check if line contains file paths."""
        for pattern in self.path_patterns:
            if re.search(pattern, line):
                return ContentBlock(
                    line, 
                    "path", 
                    0.85,
                    {"contains_path": True}
                )
        return None
    
    def _check_url(self, line: str) -> Optional[ContentBlock]:
        """Check if line contains URLs."""
        for pattern in self.url_patterns:
            if re.search(pattern, line):
                return ContentBlock(
                    line, 
                    "url", 
                    0.95,
                    {"contains_url": True}
                )
        return None
    
    def analyze_text(self, text: str) -> List[ContentBlock]:
        """
        Analyze a block of text and classify all lines.
        
        Args:
            text: Multi-line text to analyze
            
        Returns:
            List of ContentBlock objects
        """
        lines = text.split('\n')
        classified_blocks = []
        
        for line in lines:
            block = self.classify_line(line)
            classified_blocks.append(block)
        
        return classified_blocks
    
    def get_statistics(self, blocks: List[ContentBlock]) -> Dict:
        """
        Get statistics about classified content.
        
        Args:
            blocks: List of ContentBlock objects
            
        Returns:
            Dictionary with content statistics
        """
        stats = {
            "total_blocks": len(blocks),
            "content_types": {},
            "confidence_avg": 0.0
        }
        
        total_confidence = 0.0
        
        for block in blocks:
            # Count content types
            if block.content_type in stats["content_types"]:
                stats["content_types"][block.content_type] += 1
            else:
                stats["content_types"][block.content_type] = 1
            
            total_confidence += block.confidence
        
        # Calculate average confidence
        if len(blocks) > 0:
            stats["confidence_avg"] = total_confidence / len(blocks)
        
        return stats
```

## Step 2: Create a Test Script for Content Analysis

Create `test_content_analysis.py` in your project root:

```python
# test_content_analysis.py
from src.content_analyzer import ContentAnalyzer

def test_content_classification():
    """Test our content classification system."""
    
    # Create analyzer
    analyzer = ContentAnalyzer()
    
    # Test samples representing different content types
    test_samples = [
        "# Reconnaissance",
        "nmap -sV 10.10.10.1",
        "The target machine is running SSH on port 22.",
        "def exploit_function():",
        "http://10.10.10.1/admin",
        "/etc/passwd",
        "gobuster dir -u http://10.10.10.1 -w /usr/share/wordlists/common.txt",
        "1. Initial Enumeration",
        "EXPLOITATION",
        "python3 exploit.py",
        "192.168.1.100:8080",
        "C:\\Windows\\System32\\cmd.exe"
    ]
    
    print("🔍 Testing Content Classification\n")
    print("=" * 60)
    
    for sample in test_samples:
        result = analyzer.classify_line(sample)
        
        print(f"Text: {sample}")
        print(f"Type: {result.content_type}")
        print(f"Confidence: {result.confidence:.2f}")
        if result.metadata:
            print(f"Metadata: {result.metadata}")
        print("-" * 40)
    
    # Test with multi-line text
    print("\n📄 Testing Multi-line Analysis\n")
    
    sample_text = """
    # HTB Machine: Example
    
    nmap -sV 10.10.10.1
    Starting Nmap scan...
    
    The target is running the following services:
    - SSH on port 22
    - HTTP on port 80
    
    gobuster dir -u http://10.10.10.1 -w /usr/share/wordlists/common.txt
    """
    
    blocks = analyzer.analyze_text(sample_text)
    
    for i, block in enumerate(blocks):
        if block.text.strip():  # Skip empty lines for display
            print(f"{i+1:2d}. [{block.content_type:8s}] {block.text}")
    
    # Show statistics
    stats = analyzer.get_statistics(blocks)
    print(f"\n📊 Analysis Statistics:")
    print(f"Total blocks: {stats['total_blocks']}")
    print(f"Average confidence: {stats['confidence_avg']:.2f}")
    print(f"Content types found:")
    for content_type, count in stats['content_types'].items():
        print(f"  - {content_type}: {count}")

if __name__ == "__main__":
    test_content_classification()
```

## Step 3: Test Your Content Analyzer

Run the test to see how well your analyzer works:

```bash
python test_content_analysis.py
```

You should see output like:
```
🔍 Testing Content Classification

============================================================
Text: # Reconnaissance
Type: heading
Confidence: 0.80
Metadata: {'level': 2}
----------------------------------------
Text: nmap -sV 10.10.10.1
Type: command
Confidence: 0.90
Metadata: {'shell_type': 'bash'}
----------------------------------------
Text: The target machine is running SSH on port 22.
Type: network
Confidence: 0.90
Metadata: {'contains_ip': True}
----------------------------------------
```

## Step 4: Integrate with PDF Processor

Now let's combine our PDF processor with content analysis. Create `integrated_test.py`:

```python
# integrated_test.py
from src.pdf_processor import PDFProcessor
from src.content_analyzer import ContentAnalyzer

def analyze_pdf_content():
    """Test PDF extraction with content analysis."""
    
    # Initialize components
    pdf_processor = PDFProcessor()
    content_analyzer = ContentAnalyzer()
    
    # Get PDF file from user
    pdf_path = input("Enter PDF file path: ")
    
    if pdf_processor.load_pdf(pdf_path):
        print("📄 Extracting and analyzing content...\n")
        
        # Extract text from first page as example
        page_text = pdf_processor.extract_text_from_page(0)
        
        # Analyze content
        blocks = content_analyzer.analyze_text(page_text)
        
        # Display results
        print("🔍 Content Analysis Results:\n")
        print("=" * 60)
        
        for i, block in enumerate(blocks):
            if block.text.strip():  # Skip empty lines
                print(f"{i+1:2d}. [{block.content_type:8s}] {block.text[:50]}...")
                if block.metadata:
                    print(f"    Metadata: {block.metadata}")
                print()
        
        # Show statistics
        stats = content_analyzer.get_statistics(blocks)
        print(f"\n📊 Page Analysis Summary:")
        print(f"Total content blocks: {stats['total_blocks']}")
        print(f"Average confidence: {stats['confidence_avg']:.2f}")
        print(f"\nContent distribution:")
        for content_type, count in stats['content_types'].items():
            percentage = (count / stats['total_blocks']) * 100
            print(f"  {content_type:10s}: {count:3d} ({percentage:5.1f}%)")
        
        pdf_processor.close_document()

if __name__ == "__main__":
    analyze_pdf_content()
```

## Understanding What We've Built

### The ContentBlock Class

This is like a smart label that contains:
- **text**: The actual content
- **content_type**: What kind of content it is
- **confidence**: How sure we are about the classification
- **metadata**: Extra information (like programming language)

### The ContentAnalyzer Class

This is like a smart detective that can:
- **Recognize patterns**: Identify commands, code, headings, etc.
- **Assign confidence scores**: Tell us how certain it is
- **Extract metadata**: Provide additional context
- **Generate statistics**: Summarize the analysis

### Pattern Recognition

Our analyzer uses **regular expressions** (regex) to identify patterns:
- Commands start with tool names or have specific syntax
- Code has function definitions or import statements
- IP addresses follow a specific number pattern
- Headings are usually short and in title case

## Common Issues and Improvements

### Issue: False Positives
**Example**: "The nmap command" classified as a command
**Solution**: Make patterns more specific, require commands to start at line beginning

### Issue: Missing Content Types
**Example**: SQL queries not recognized
**Solution**: Add more patterns for different content types

### Issue: Low Confidence Scores
**Solution**: Fine-tune patterns and add more specific rules

## What We've Accomplished

🎉 **Great progress!** You now have:
- ✅ Smart content classification system
- ✅ Pattern recognition for HTB-specific content
- ✅ Confidence scoring for classifications
- ✅ Metadata extraction for additional context
- ✅ Integration with PDF processing
- ✅ Statistical analysis of content

## What's Next?

In Phase 3, we'll use these classifications to generate properly formatted markdown:
- Convert headings to `#` syntax
- Wrap commands in code blocks with language tags
- Format lists and emphasis properly
- Create clean, readable markdown output

Your content analyzer will be the brain that tells the markdown generator exactly how to format each piece of content!

---

[← Previous: Phase 1 - Basic PDF Extraction](04-phase1-basic-pdf-extraction.md) | [Next: Phase 3 - Markdown Generation →](06-phase3-markdown-generation.md)
