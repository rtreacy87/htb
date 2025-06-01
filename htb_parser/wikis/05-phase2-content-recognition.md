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


````
+------------------------------------------+
|           ContentAnalyzer                |
+------------------------------------------+
| - command_patterns: List[str]            |
| - code_patterns: List[str]               |
| - network_patterns: List[str]            |
| - path_patterns: List[str]               |
| - url_patterns: List[str]                |
| - heading_patterns: List[str]            |
+------------------------------------------+
| + __init__()                             |
| + _setup_patterns()                      |
| + classify_line(line: str) -> ContentBlock|
| + _check_command(line: str) -> ContentBlock|
| + _check_code(line: str) -> ContentBlock |
| + _check_heading(line: str) -> ContentBlock|
| + _check_network(line: str) -> ContentBlock|
| + _check_path(line: str) -> ContentBlock |
| + _check_url(line: str) -> ContentBlock  |
| + analyze_text(text: str) -> List[ContentBlock]|
| + get_statistics(blocks: List[ContentBlock]) -> Dict|
+------------------------------------------+
              |
              | creates
              v
+------------------------------------------+
|            ContentBlock                  |
+------------------------------------------+
| - text: str                              |
| - content_type: str                      |
| - confidence: float                      |
| - metadata: Dict                         |
+------------------------------------------+
| + __post_init__()                        |
+------------------------------------------+

INPUT:
+------------------------------------------+
|           Raw PDF Text                   |
+------------------------------------------+
| "# Reconnaissance                        |
|  nmap -sV 10.10.10.1                     |
|  The target is running SSH on port 22"   |
+------------------------------------------+
              |
              | fed into
              v
+------------------------------------------+
|           ContentAnalyzer                |
+------------------------------------------+
              |
              | produces
              v
+------------------------------------------+
|        List[ContentBlock]                |
+------------------------------------------+
| ContentBlock("# Reconnaissance",         |
|              "heading", 0.9,             |
|              {"level": 1})               |
|                                          |
| ContentBlock("nmap -sV 10.10.10.1",      |
|              "command", 0.95,            |
|              {"shell_type": "bash"})     |
|                                          |
| ContentBlock("The target is running...", |
|              "text", 0.8,                |
|              {"contains_network": True}) |
+------------------------------------------+
````

## Executive Summary: ContentAnalyzer System

The ContentAnalyzer system provides intelligent text classification for HTB (Hack The Box) PDF parsing, consisting of two key components:

1. **ContentAnalyzer**: A sophisticated pattern recognition engine that:
   - Identifies various content types (commands, code, headings, etc.)
   - Uses regex pattern matching for classification
   - Processes text line-by-line with confidence scoring
   - Provides statistical analysis of content distribution

2. **ContentBlock**: A data container that:
   - Stores classified text with its identified type
   - Includes confidence scores for classification accuracy
   - Contains metadata for additional context
   - Serves as the foundation for markdown generation

This system transforms raw extracted PDF text into structured, classified content blocks that enable intelligent markdown conversion while preserving the semantic meaning of different content types found in HTB machine walkthroughs.


**ContentBlock Class**

The code defines a `ContentBlock` dataclass that serves as a container for classified text content. Each block stores:

1. The original text string
2. A content type classification (e.g., "command", "code", "heading")
3. A confidence score indicating classification certainty
4. Optional metadata dictionary for additional context

The class includes a `__post_init__` method that initializes an empty dictionary if no metadata is provided, ensuring the metadata attribute is never None. This simple but essential data structure forms the foundation for the HTB parser's content classification system.

#### Difference Between `__init__` and `__post_init__`

##### `__init__`
- Standard Python initialization method that runs when an object is created
- Handles the initial assignment of attributes from constructor arguments
- In regular classes, this is where you'd set default values and validate inputs
- In dataclasses, this is automatically generated to set the fields

##### `__post_init__`
- Special method in dataclasses that runs immediately after `__init__` completes
- Allows for additional processing after all fields have been initialized
- Perfect for validation, derived fields, or complex initialization logic
- Runs automatically when a dataclass instance is created, but only if defined

In the `ContentBlock` class, `__post_init__` ensures the `metadata` field is never `None` by initializing it to an empty dictionary if needed. This happens after the automatic field initialization but before the object is fully constructed.


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

```
### Python Dataclasses

A dataclass is a special type of class introduced in Python 3.7 through the `dataclasses` module that automatically generates common boilerplate code for you.

#### Key Benefits

1. **Reduced Boilerplate**: Automatically generates `__init__()`, `__repr__()`, `__eq__()` and other special methods
2. **Cleaner Code**: Focuses on data structure rather than implementation details
3. **Type Annotations**: Encourages use of type hints for better code documentation
4. **Immutability Option**: Can create frozen (immutable) instances with `frozen=True`

#### Example

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

This simple declaration automatically creates initialization, string representation, and equality comparison methods.

#### Why Important for ContentBlock

For the `ContentBlock` class, dataclasses are ideal because:

1. The class primarily stores data with minimal behavior
2. It needs clear type definitions for its fields
3. The automatic `__repr__()` makes debugging easier
4. The `__post_init__()` hook allows for custom initialization logic

This makes the code more maintainable and focused on the actual data structure rather than implementation details.

| Special Method    | Description                                           | Why Important for ContentBlock                                                                                |
|-------------------|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| `__init__()`      | Constructor method that initializes object attributes | Automatically handles setting `text`, `content_type`, `confidence`, and `metadata` from constructor arguments |
| `__repr__()`      | Returns string representation of the object           | Makes debugging easier by showing all fields when printing a ContentBlock instance                            |
| `__eq__()`        | Defines equality comparison between objects           | Allows comparing ContentBlocks based on their field values rather than object identity                        |
| `__post_init__()` | Runs after automatic initialization                   | Ensures `metadata` is never `None` by defaulting to empty dictionary                                          |

1. The ContentAnalyzer analyzes text and creates ContentBlock instances to represent classified content.

2. The ContentBlock class is a data container that holds:
   - The original text
   - Its classified type (command, code, heading, etc.)
   - A confidence score
   - Optional metadata

3. The `__post_init__` method in ContentBlock ensures that if a ContentBlock is created with `metadata=None`, it will automatically initialize an empty dictionary `{}` instead.

4. This happens regardless of what characteristics were found in the text - it's just ensuring that the metadata field is never None, which prevents potential errors when code tries to access metadata attributes.

So it's not about returning an empty dictionary when characteristics aren't found - it's about ensuring the metadata attribute is always a dictionary (even if empty) rather than None, which makes the ContentBlock more robust and easier to work with.


The `ContentAnalyzer` class is responsible for classifying text into different content types. It uses regex patterns to identify commands, code, headings, and other elements. The `classify_line` method processes each line of text and returns a `ContentBlock` object with the classification results.

The ContentAnalyzer class does have inputs, but they're provided through method parameters rather than being stored as class attributes. Here's how it works:

1. The ContentAnalyzer class has an `analyze_text(text: str)` method that takes a string input parameter.

2. This method processes the input text (typically extracted from a PDF) line by line.

3. For each line, it calls the `classify_line(line: str)` method, which analyzes the line and returns a ContentBlock.

4. The input text itself isn't stored as a class attribute because:
   - The analyzer is stateless - it doesn't need to remember previous texts
   - This allows processing multiple different texts with the same analyzer instance
   - It follows the functional programming principle of separating data from operations

The typical usage pattern would be:

```python
# Create analyzer
analyzer = ContentAnalyzer()

# Process text (input comes from outside)
pdf_text = pdf_processor.extract_text()
content_blocks = analyzer.analyze_text(pdf_text)

# Use the resulting content blocks
for block in content_blocks:
    print(f"{block.content_type}: {block.text}")
```

This design makes the ContentAnalyzer more flexible and reusable across different text sources.

```
+------------------------------------------+
|           Input Text File                |
+------------------------------------------+
| "# Reconnaissance                        |
|  nmap -sV 10.10.10.1                     |
|  The target is running SSH on port 22"   |
+------------------------------------------+
              |
              | read by external code
              v
+------------------------------------------+
|           PDF Processor                  |
+------------------------------------------+
| + extract_text() -> str                  |
+------------------------------------------+
              |
              | returns extracted text
              v
+------------------------------------------+
|           Raw Text String                |
+------------------------------------------+
| "# Reconnaissance\n                      |
|  nmap -sV 10.10.10.1\n                   |
|  The target is running SSH on port 22"   |
+------------------------------------------+
              |
              | passed to
              v
+------------------------------------------+
|        ContentAnalyzer.analyze_text()    |
+------------------------------------------+
| 1. Split text into lines                 |
| 2. Process each line:                    |
|    a. Call classify_line() on each line  |
|    b. Apply pattern matching             |
|    c. Determine content type             |
|    d. Calculate confidence score         |
|    e. Extract metadata                   |
| 3. Return list of ContentBlocks          |
+------------------------------------------+
              |
              | produces
              v
+------------------------------------------+
|        List[ContentBlock]                |
+------------------------------------------+
| ContentBlock("# Reconnaissance",         |
|              "heading", 0.9,             |
|              {"level": 1})               |
|                                          |
| ContentBlock("nmap -sV 10.10.10.1",      |
|              "command", 0.95,            |
|              {"shell_type": "bash"})     |
|                                          |
| ContentBlock("The target is running...", |
|              "text", 0.8,                |
|              {"contains_network": True}) |
+------------------------------------------+
              |
              | passed to
              v
+------------------------------------------+
|        Markdown Generator                |
+------------------------------------------+
| Converts ContentBlocks to markdown       |
+------------------------------------------+
              |
              | produces
              v
+------------------------------------------+
|        Markdown Output                   |
+------------------------------------------+
| # Reconnaissance                         |
|                                          |
| ```bash                                  |
| nmap -sV 10.10.10.1                      |
| ```                                      |
|                                          |
| The target is running SSH on port 22     |
+------------------------------------------+
```
 Since the ContentAnalyzer is stateless, it can be used to analyze multiple texts independently. The PDFProcessor can call analyze_text() for each PDF it processes, and the ContentAnalyzer will handle each one separately. Thus when it is initilized the `__init__` method is called only the setup paterns are defined in the class attributes.

```python
class ContentAnalyzer:
    """
    Analyzes extracted text and classifies different content types.
    
    This is like a smart librarian that can look at text and 
    immediately know what category it belongs to.
    """
    
    def __init__(self):
        """Initialize the content analyzer with pattern definitions."""
        self._setup_patterns()
```
The internal method `_setup_patterns` is called to define the regex patterns for different content types. There are six types of content that are defined in the `_setup_patterns` method.

| Pattern Type           | Purpose                               | Examples                                             | Why Important                                                                                                   |
|------------------------|---------------------------------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| **Command Patterns**   | Identify shell commands and tools     | `nmap -sV`, `sudo apt-get`, `$ ls -la`               | Formats commands with proper syntax highlighting and preserves command structure for readers to follow along    |
| **Code Patterns**      | Detect programming language snippets  | `def function()`, `public class`, `import module`    | Ensures code is properly formatted with language-specific syntax highlighting for readability and execution     |
| **Network Patterns**   | Recognize network-related information | IP addresses, ports, IPv6 addresses                  | Helps identify technical network details that are crucial for penetration testing documentation                 |
| **File Path Patterns** | Identify filesystem references        | `/etc/passwd`, `C:\Windows\System32`, `~/Documents`  | Preserves path formatting and highlights important file locations that may be targets or contain sensitive data |
| **URL Patterns**       | Detect web addresses and endpoints    | `https://example.com`, `ftp://server.local`          | Ensures URLs are properly formatted and potentially made clickable in the final documentation                   |
| **Heading Patterns**   | Identify section titles and headers   | `ENUMERATION`, `1. Reconnaissance`, `Initial Access` | Creates proper document structure with hierarchical headings for better organization and navigation             |

These pattern types form a comprehensive classification system specifically designed for HTB (Hack The Box) machine writeups. They capture the most common and important elements found in penetration testing documentation, ensuring that the final markdown output maintains proper formatting, syntax highlighting, and structural organization. 

The patterns are prioritized in the classification process, with commands and code given higher priority since they require specific formatting. This classification system allows the parser to transform raw text into semantically meaningful content blocks that preserve the technical details and instructional nature of security testing documentation.

```python
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
```
The `classify_line` method is the main method that is called to classify a single line of text. It takes a string input parameter and returns a `ContentBlock` object with the classification results. The method first checks for commands, then code, then headings, then network elements, then file paths, then URLs, and finally defaults to regular text if none of the other checks match. It is setup in an if return method to make it easier to read,understand and update.

```python
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
```


1. The `classify_line` method is the main entry point that receives a line of text.

2. It calls `_check_command` **first** (before any determination is made) to see if the line matches any command patterns.

3. If `_check_command` finds a match:
   - It calls `_determine_shell_type` to figure out if it's a Python, PHP, or Bash command
   - It creates and returns a ContentBlock with type "command"
   - The `classify_line` method immediately returns this ContentBlock

4. If `_check_command` returns None (no match), then `classify_line` continues to check for other content types (code, heading, etc.)

So the process is:
1. Try to match as command first
2. If it's a command, determine what type of shell command it is
3. Only if it's not a command, continue checking other content types

The `_determine_shell_type` method - it checks if the command starts with "python" or "php", and defaults to "bash" if neither is found.


```
+------------------------------------------+
|           Input Line                     |
+------------------------------------------+
| "nmap -sV 10.10.10.1"                    |
+------------------------------------------+
              |
              | passed to
              v
+------------------------------------------+
|        classify_line(line)               |
+------------------------------------------+
              |
              | calls first check
              v
+------------------------------------------+
|        _check_command(line)              |
+------------------------------------------+
              |
              | calls
              v
+------------------------------------------+
|   _line_matches_command_pattern(line)    |
+------------------------------------------+
| 1. Iterate through command_patterns      |
| 2. For each pattern:                     |
|    a. Apply re.match with IGNORECASE     |
|    b. If any match found, return True    |
| 3. If no match, return False             |
+------------------------------------------+
              |
              | if pattern matches?
              v
        ┌─────┴─────┐
        │           │
      True        False
        │           │
        v           v
+------------------+ +------------------+
| _determine_shell_| | Return None      |
| _type(line)      | | (Not a command)  |
+------------------+ +------------------+
| 1. Check python  |         |
| 2. Check php     |         |
| 3. Return bash   |         |
+------------------+         |
        |                    |
        v                    |
+------------------+         |
| ContentBlock     |         |
| Creation         |         |
+------------------+         |
        |                    |
        v                    |
+------------------------------------------+
|        classify_line continues           |
+------------------------------------------+
| If None returned, check for other types: |
| - Check for code                         |
| - Check for heading                      |
| - Check for network elements             |
| - etc.                                   |
+------------------------------------------+
```

```python
    def _check_command(self, line: str) -> Optional[ContentBlock]:
        """Check if line is a command."""
        if self._line_matches_command_pattern(line):               
            shell_type = self._determine_shell_type(line)                
            return ContentBlock(
                line, 
                "command", 
                0.9,
                {"shell_type": shell_type}
            )
        return None

    def _line_matches_command_pattern(self, line: str) -> bool:
        """Check if line matches any command pattern."""
        for pattern in self.command_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False

    def _determine_shell_type(self, line: str) -> str:    
        """Determine the type of shell based on the command."""
        if line.startswith("python"):
            return "python"
        elif line.startswith("php"):
            return "php"
        else:
            return "bash"
```
The `_check_code` method checks if the line matches any code patterns. If it does, it determines the language based on specific keywords and returns a ContentBlock with type "code".

```python
    def _check_code(self, line: str) -> Optional[ContentBlock]:
        """Check if line is code."""
        if self._line_matches_code_pattern(line):
            language = self._determine_code_language(line)                
                return ContentBlock(
                    line, 
                    "code", 
                    0.85,
                    {"language": language}
                )
        return None
    
    def _line_matches_code_pattern(self, line: str) -> bool:
        """Check if line matches any code pattern."""
        for pattern in self.code_patterns:
            if re.search(pattern, line):
                return True
        return False

    def _determine_code_language(self, line: str) -> str:
        """Determine the language of the code."""
        if "def " in line:
            return "python"
        if "function " in line:
            return "javascript"
        if "<?php" in line:
            return "php"
        if "public class" in line:
            return "java"
        return "unknown"
```
The `_check_heading` method checks if the line matches any heading patterns. If it does, it determines the heading level based on characteristics like the presence of numbers or all caps. It returns a ContentBlock with type "heading".

```python
    def _check_heading(self, line: str) -> Optional[ContentBlock]:
        """Check if line is a heading."""
        # Skip very long lines (unlikely to be headings)
        if len(line) > 100:
            return None
        if self._line_matches_heading_pattern(line):
            level = self._determine_heading_level(line)
            return ContentBlock(
                line, 
                "heading", 
                0.8,
                {"level": level}
            )
        return None
     
    def _line_matches_heading_pattern(self, line: str) -> bool:
        """Check if line matches any heading pattern."""
        for pattern in self.heading_patterns:
            if re.match(pattern, line):
                return True
        return False

    def _determine_heading_level(self, line: str) -> int:
        """Determine the level of the heading."""
        if re.match(r'^[0-9]+\.', line):
            return 2  # Numbered sections are usually H2
        elif line.isupper() and len(line) < 30:
            return 1  # Short ALL CAPS are usually H1
        else:
            return 2  # Default to H2
```
The `_check_network` method checks if the line matches any network patterns. If it does, it returns a ContentBlock with type "network".

```python
    def _check_network(self, line: str) -> Optional[ContentBlock]:
        """Check if line contains network information."""
        if self._line_matches_network_pattern(line):
                return ContentBlock(
                    line, 
                    "network", 
                    0.9,
                    {"contains_ip": True}
                )
        return None
    
    def _line_matches_network_pattern(self, line: str) -> bool:
        """Check if line matches any network pattern."""
        for pattern in self.network_patterns:
            if re.search(pattern, line):
                return True
        return False
```

The `_check_path` and `_check_url` methods work similarly, checking for file paths and URLs respectively. If a match is found, they return a ContentBlock with type "path" or "url".

```python
    def _check_path(self, line: str) -> Optional[ContentBlock]:
        """Check if line contains file paths."""
        if self._line_matches_path_pattern(line): 
            return ContentBlock(
                    line, 
                    "path", 
                    0.85,
                    {"contains_path": True}
                )
        return None
    
        def _line_matches_path_pattern(self, line: str) -> bool:
        """Check if line matches any path pattern."""
        for pattern in self.path_patterns:
            if re.search(pattern, line):
                return True
        return False
```
The `_check_url` method checks if the line matches any URL patterns. If it does, it returns a ContentBlock with type "url".

```python
    def _check_url(self, line: str) -> Optional[ContentBlock]:
        """Check if line contains URLs."""
        if self._line_matches_url_pattern(line):
            return ContentBlock(
                    line, 
                    "url", 
                    0.95,
                    {"contains_url": True}
                )
        return None
    
    def _line_matches_url_pattern(self, line: str) -> bool:
        """Check if line matches any URL pattern."""
        for pattern in self.url_patterns:
            if re.search(pattern, line):
                return True
        return False
```
The `analyze_text` method takes a multi-line text input and classifies each line. It returns a list of ContentBlock objects.
```python
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
    
```
The `get_statistics` method analyzes a list of `ContentBlock` objects and generates statistical information about them. It calculates:

1. The total number of content blocks
2. A count of each content type (like commands, code, headings, etc.)
3. The average confidence score across all blocks

This provides a useful summary of the content classification results, helping to understand the composition and reliability of the analyzed content.


```python
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

Here's a detailed breakdown:

1. **Initialization**: 
   - Creates a `stats` dictionary with three keys: `total_blocks`, `content_types` (empty dictionary), and `confidence_avg` (initialized to 0.0)
   - Sets `total_blocks` to the length of the input list
   - Initializes a variable `total_confidence` to track the sum of confidence scores

2. **Content Type Counting**:
   - Iterates through each `ContentBlock` in the input list
   - For each block, checks if its `content_type` already exists in the `content_types` dictionary
   - If it exists, increments the count for that type
   - If not, adds the type to the dictionary with an initial count of 1
   - Simultaneously accumulates the confidence score of each block

3. **Average Confidence Calculation**:
   - After processing all blocks, checks if there are any blocks (to avoid division by zero)
   - If blocks exist, calculates the average confidence by dividing the total confidence by the number of blocks
   - Stores this value in the `confidence_avg` field of the stats dictionary

4. **Return Value**:
   - Returns the completed stats dictionary containing the total count, type distribution, and average confidence

This method efficiently processes the blocks in a single pass, making it O(n) in time complexity where n is the number of blocks.

**Note**:
The `get_statistics` method doesn't check if you've identified all possible content types or if you're missing categories. It simply counts what's already been classified.

The method works with whatever content types are present in your existing `ContentBlock` objects. It doesn't validate against a predefined list of expected categories or alert you to missing ones.

If you want to check for missing categories, you would need to:

1. Define a complete list of expected content types
2. Compare that list against the keys in the `content_types` dictionary
3. Identify any expected types that aren't present in your results

For example, you could add code like this after the current implementation:

```python
def check_for_missing_categories(self, stats: Dict) -> List[str]:
    """Check if any expected content types are missing from results."""
    expected_types = ["command", "code", "heading", "network", "path", "url", "text"]
    found_types = stats["content_types"].keys()
    missing_types = [t for t in expected_types if t not in found_types]
    return missing_types
```

This would help you identify if your content blocks are missing any expected categories, which could indicate either:
1. Your analyzer isn't correctly identifying certain content types
2. The analyzed document genuinely doesn't contain examples of those content types


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
Here is an example of the output:

```bash
Testing Content Classification

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
Text: def exploit_function():
Type: code
Confidence: 0.85
Metadata: {'language': 'python'}
----------------------------------------
Text: http://10.10.10.1/admin
Type: url
Confidence: 0.95
Metadata: {'contains_url': True}
----------------------------------------
Text: /etc/passwd
Type: path
Confidence: 0.85
Metadata: {'contains_path': True}
----------------------------------------
Text: gobuster dir -u http://10.10.10.1 -w /usr/share/wordlists/common.txt
Type: command
Confidence: 0.90
Metadata: {'shell_type': 'bash'}
----------------------------------------
Text: 1. Initial Enumeration
Type: heading
Confidence: 0.80
Metadata: {'level': 2}
----------------------------------------
Text: EXPLOITATION
Type: heading
Confidence: 0.80
Metadata: {'level': 1}
----------------------------------------
Text: python3 exploit.py
Type: command
Confidence: 0.90
Metadata: {'shell_type': 'python'}
----------------------------------------
Text: 192.168.1.100:8080
Type: network
Confidence: 0.90
Metadata: {'contains_ip': True}
----------------------------------------
Text: C:\Windows\System32\cmd.exe
Type: path
Confidence: 0.85
Metadata: {'contains_path': True}
----------------------------------------

Testing Multi-line Analysis

 2. [heading ] # HTB Machine: Example
 4. [command ] nmap -sV 10.10.10.1
 5. [text    ] Starting Nmap scan...
 7. [text    ] The target is running the following services:
 8. [network ] - SSH on port 22
 9. [network ] - HTTP on port 80
11. [command ] gobuster dir -u http://10.10.10.1 -w /usr/share/wordlists/common.txt

Analysis Statistics:
Total blocks: 12
Average confidence: 0.92
Content types found:
  - empty: 5
  - heading: 1
  - command: 2
  - text: 2
  - network: 2
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
