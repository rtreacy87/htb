# Phase 3: Markdown Generation

## What We're Building in This Phase

Now that we can extract text and classify content types, it's time to create the final piece - converting our classified content into beautiful, properly formatted markdown!

## Learning Objectives

By the end of this phase, you'll have:
- A markdown generator that converts classified content to proper markdown
- Support for all major markdown elements (headings, code blocks, lists, etc.)
- Clean, readable output optimized for LLM consumption
- A complete working parser from PDF to markdown

## Understanding Markdown Generation

### From Classification to Markdown

Our content analyzer gives us classified blocks like:
```python
ContentBlock(text="nmap -sV 10.10.10.1", content_type="command", confidence=0.9)
```

We need to convert this to:
```markdown
```bash
nmap -sV 10.10.10.1
```
```

### Markdown Elements We'll Generate

1. **Headings**: `#`, `##`, `###` for different levels
2. **Code blocks**: Fenced with language tags
3. **Inline code**: For short commands or paths
4. **Lists**: Ordered and unordered
5. **Emphasis**: Bold and italic text
6. **Links**: Clickable URLs
7. **Line breaks**: Proper spacing

## Step 1: Create the Markdown Generator

Create a new file `src/markdown_generator.py`:

```python
# src/markdown_generator.py
from typing import List, Dict, Optional
from src.content_analyzer import ContentBlock

class MarkdownGenerator:
    """
    Converts classified content blocks into properly formatted markdown.
    
    This is like a skilled translator that knows exactly how to 
    format each type of content in markdown.
    """
    
    def __init__(self):
        """Initialize the markdown generator with formatting rules."""
        self.setup_formatting_rules()
    
    def setup_formatting_rules(self):
        """Define how each content type should be formatted."""
        
        # Language mappings for code blocks
        self.language_mappings = {
            "bash": ["nmap", "gobuster", "dirb", "nikto", "curl", "wget"],
            "python": ["python", "python3", "pip"],
            "sql": ["select", "insert", "update", "delete", "union"],
            "php": ["<?php", "php"],
            "javascript": ["function", "var", "let", "const"],
            "powershell": ["powershell", "ps1"],
        }
        
        # Inline vs block code thresholds
        self.inline_code_max_length = 50
        
        # Heading level mappings
        self.heading_keywords = {
            1: ["reconnaissance", "enumeration", "exploitation", "privilege escalation", "conclusion"],
            2: ["initial scan", "service enumeration", "web enumeration", "vulnerability assessment"],
            3: ["port scan", "directory enumeration", "subdomain enumeration"]
        }
    
    def generate_markdown(self, content_blocks: List[ContentBlock]) -> str:
        """
        Convert a list of content blocks to markdown.
        
        Args:
            content_blocks: List of classified content blocks
            
        Returns:
            Formatted markdown string
        """
        markdown_lines = []
        previous_block_type = None
        
        for i, block in enumerate(content_blocks):
            # Skip empty blocks
            if not block.text.strip():
                # Add spacing between sections
                if previous_block_type and previous_block_type != "empty":
                    markdown_lines.append("")
                continue
            
            # Generate markdown for this block
            markdown_content = self._format_block(block)
            
            # Add appropriate spacing
            if self._needs_spacing(previous_block_type, block.content_type):
                markdown_lines.append("")
            
            markdown_lines.append(markdown_content)
            previous_block_type = block.content_type
        
        return "\n".join(markdown_lines)
    
    def _format_block(self, block: ContentBlock) -> str:
        """Format a single content block based on its type."""
        
        if block.content_type == "heading":
            return self._format_heading(block)
        
        elif block.content_type == "command":
            return self._format_command(block)
        
        elif block.content_type == "code":
            return self._format_code(block)
        
        elif block.content_type == "network":
            return self._format_network(block)
        
        elif block.content_type == "path":
            return self._format_path(block)
        
        elif block.content_type == "url":
            return self._format_url(block)
        
        else:  # Regular text
            return self._format_text(block)
    
    def _format_heading(self, block: ContentBlock) -> str:
        """Format heading blocks."""
        text = block.text.strip()
        
        # Remove common prefixes
        text = text.lstrip("#").strip()
        text = text.lstrip("0123456789.").strip()
        
        # Determine heading level
        level = block.metadata.get("level", 2)
        
        # Adjust level based on content
        text_lower = text.lower()
        for check_level, keywords in self.heading_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                level = check_level
                break
        
        # Ensure level is between 1 and 6
        level = max(1, min(6, level))
        
        return f"{'#' * level} {text}"
    
    def _format_command(self, block: ContentBlock) -> str:
        """Format command blocks."""
        text = block.text.strip()
        
        # Remove shell prompts
        text = text.lstrip("$#").strip()
        
        # Determine language
        language = self._detect_command_language(text)
        
        # Use inline code for very short commands
        if len(text) <= self.inline_code_max_length and "\n" not in text:
            return f"`{text}`"
        
        # Use code block for longer commands
        return f"```{language}\n{text}\n```"
    
    def _format_code(self, block: ContentBlock) -> str:
        """Format code blocks."""
        text = block.text.strip()
        language = block.metadata.get("language", "")
        
        # Use inline code for short snippets
        if len(text) <= self.inline_code_max_length and "\n" not in text:
            return f"`{text}`"
        
        # Use code block for longer code
        return f"```{language}\n{text}\n```"
    
    def _format_network(self, block: ContentBlock) -> str:
        """Format network-related content."""
        text = block.text.strip()
        
        # Check if it's just an IP or if it's part of a sentence
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]+)?\b'
        
        if re.fullmatch(ip_pattern, text):
            # Just an IP address - use inline code
            return f"`{text}`"
        else:
            # IP within text - highlight the IP
            highlighted = re.sub(ip_pattern, r'`\g<0>`', text)
            return highlighted
    
    def _format_path(self, block: ContentBlock) -> str:
        """Format file path content."""
        text = block.text.strip()
        
        # Check if it's just a path or part of a sentence
        import re
        path_patterns = [
            r'^/[a-zA-Z0-9_\-\./]+$',  # Unix path only
            r'^[A-Za-z]:\\[a-zA-Z0-9_\-\\\./]+$',  # Windows path only
            r'^~/[a-zA-Z0-9_\-\./]*$',  # Home directory path only
        ]
        
        is_path_only = any(re.match(pattern, text) for pattern in path_patterns)
        
        if is_path_only:
            return f"`{text}`"
        else:
            # Path within text - highlight paths
            highlighted = text
            for pattern in [r'/[a-zA-Z0-9_\-\./]+', r'[A-Za-z]:\\[a-zA-Z0-9_\-\\\./]+', r'~/[a-zA-Z0-9_\-\./]*']:
                highlighted = re.sub(pattern, r'`\g<0>`', highlighted)
            return highlighted
    
    def _format_url(self, block: ContentBlock) -> str:
        """Format URL content."""
        text = block.text.strip()
        
        # Extract URLs and make them clickable
        import re
        url_pattern = r'(https?://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+)'
        
        # Replace URLs with markdown links
        def make_link(match):
            url = match.group(1)
            return f"[{url}]({url})"
        
        formatted = re.sub(url_pattern, make_link, text)
        return formatted
    
    def _format_text(self, block: ContentBlock) -> str:
        """Format regular text content."""
        text = block.text.strip()
        
        # Apply basic formatting enhancements
        # Bold for important terms
        important_terms = ["important", "note", "warning", "critical", "vulnerable", "exploit"]
        for term in important_terms:
            pattern = rf'\b({term})\b'
            text = re.sub(pattern, r'**\1**', text, flags=re.IGNORECASE)
        
        return text
    
    def _detect_command_language(self, command: str) -> str:
        """Detect the appropriate language tag for a command."""
        command_lower = command.lower()
        
        for language, tools in self.language_mappings.items():
            if any(tool in command_lower for tool in tools):
                return language
        
        # Default to bash for unknown commands
        return "bash"
    
    def _needs_spacing(self, previous_type: Optional[str], current_type: str) -> bool:
        """Determine if spacing is needed between content blocks."""
        
        # Always add space before headings
        if current_type == "heading":
            return True
        
        # Add space after headings
        if previous_type == "heading":
            return True
        
        # Add space between different content types
        if previous_type and previous_type != current_type:
            # Exception: don't add space between text and network/path/url
            if previous_type == "text" and current_type in ["network", "path", "url"]:
                return False
            return True
        
        return False
    
    def add_document_metadata(self, title: str = "", author: str = "", date: str = "") -> str:
        """Generate markdown document header with metadata."""
        
        header_lines = []
        
        if title:
            header_lines.append(f"# {title}")
            header_lines.append("")
        
        if author or date:
            header_lines.append("---")
            if author:
                header_lines.append(f"**Author:** {author}")
            if date:
                header_lines.append(f"**Date:** {date}")
            header_lines.append("---")
            header_lines.append("")
        
        return "\n".join(header_lines)
    
    def generate_table_of_contents(self, content_blocks: List[ContentBlock]) -> str:
        """Generate a table of contents from headings."""
        
        toc_lines = ["## Table of Contents", ""]
        
        for block in content_blocks:
            if block.content_type == "heading":
                level = block.metadata.get("level", 2)
                text = block.text.strip().lstrip("#").strip()
                
                # Create anchor link
                anchor = text.lower().replace(" ", "-").replace(".", "")
                indent = "  " * (level - 1)
                
                toc_lines.append(f"{indent}- [{text}](#{anchor})")
        
        toc_lines.append("")
        return "\n".join(toc_lines)
```

## Step 2: Create a Complete Parser Test

Now let's create a test that combines all our components. Create `complete_parser_test.py`:

```python
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
```

## Step 3: Test Your Complete Parser

Run your complete parser:

```bash
python complete_parser_test.py
```

You should see something like:
```
Enter PDF file path: sample_writeup.pdf
Enter output markdown file path (e.g., output.md): my_writeup.md

📄 Processing PDF...
✅ Successfully loaded PDF: sample_writeup.pdf
   Pages: 5

🔍 Analyzing content...
📝 Generating markdown...
✅ Markdown saved to my_writeup.md

📊 Conversion Statistics:
Total content blocks: 156
Average confidence: 0.87
Output file size: 8432 characters

Content breakdown:
  text      :  89 ( 57.1%)
  command   :  23 ( 14.7%)
  heading   :  12 (  7.7%)
  network   :  18 ( 11.5%)
  code      :   8 (  5.1%)
  path      :   6 (  3.8%)
```

## Step 4: Examine Your Output

Open the generated markdown file. You should see:

```markdown
# HTB Writeup - Example Machine

---
**Author:** Security Researcher
**Date:** 2024-01-15
---

## Table of Contents

- [Reconnaissance](#reconnaissance)
  - [Initial Scan](#initial-scan)
  - [Service Enumeration](#service-enumeration)
- [Exploitation](#exploitation)
- [Privilege Escalation](#privilege-escalation)

# Reconnaissance

## Initial Scan

First, let's scan the target machine to identify open ports:

```bash
nmap -sV 10.10.10.1
```

The scan reveals several **important** services running:
- SSH on port `22`
- HTTP on port `80`
- MySQL on port `3306`

## Service Enumeration

Let's enumerate the web service:

```bash
gobuster dir -u http://10.10.10.1 -w /usr/share/wordlists/common.txt
```

This reveals several interesting directories including `/admin` and `/backup`.
```

## Understanding the Output Quality

### What's Working Well:
- ✅ Proper heading hierarchy
- ✅ Code blocks with language tags
- ✅ Inline code for short commands
- ✅ Bold text for important terms
- ✅ Table of contents generation
- ✅ Document metadata

### Areas for Improvement:
- Some text might still be misclassified
- Complex layouts might need manual review
- OCR text might have artifacts

## Advanced Features

### Custom Formatting Rules

You can customize the markdown generator by modifying the formatting rules:

```python
# Add custom language mappings
self.language_mappings["custom"] = ["mytool", "customcommand"]

# Add custom heading keywords
self.heading_keywords[1].append("my custom section")
```

### Post-Processing Hooks

Add custom post-processing:

```python
def custom_post_process(self, markdown: str) -> str:
    """Apply custom post-processing rules."""
    # Remove excessive blank lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    # Fix common OCR errors
    markdown = markdown.replace("1", "l")  # Example fix
    
    return markdown
```

## What We've Accomplished

🎉 **Fantastic work!** You now have a complete PDF to Markdown parser that:

- ✅ Extracts text from PDFs
- ✅ Classifies content intelligently
- ✅ Generates clean, properly formatted markdown
- ✅ Includes document metadata and table of contents
- ✅ Handles commands, code, headings, and technical content
- ✅ Provides detailed statistics and confidence scores

## What's Next?

In Phase 4, we'll add advanced features:
- OCR for image-heavy documents
- Better handling of complex layouts
- Batch processing capabilities
- Quality validation and error correction

Your parser is already functional and useful - the next phase will make it even more powerful!

---

[← Previous: Phase 2 - Content Recognition](05-phase2-content-recognition.md) | [Next: Phase 4 - Advanced Features →](07-phase4-advanced-features.md)
