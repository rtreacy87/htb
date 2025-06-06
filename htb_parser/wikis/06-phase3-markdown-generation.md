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
````markdown
```bash
nmap -sV 10.10.10.1
```
````

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

The `MarkdownGenerator` class transforms classified content blocks into properly formatted markdown. It:

1. **Converts different content types** into appropriate markdown formats:
   - Headings → `# Heading`
   - Commands → ```bash code blocks
   - Code → Language-specific code blocks
   - Network info → Inline code for IPs
   - Paths → Inline code for file paths
   - URLs → Markdown links

2. **Applies intelligent formatting rules**:
   - Uses language detection for code blocks
   - Determines heading levels based on content
   - Chooses between inline code vs. code blocks based on length
   - Highlights technical terms in regular text

3. **Manages document structure**:
   - Adds proper spacing between sections
   - Generates document metadata headers
   - Creates table of contents from headings
   - Ensures consistent formatting throughout

4. **Provides customization options** for formatting rules and language mappings

The class acts as a "translator" that converts structured content into clean, readable markdown optimized for technical documentation.
```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|   PDF Document   |---->|  PDF Processor   |---->| Content Analyzer |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                          |                        |
                          | extract_all_text()     | analyze_text()
                          ↓                        ↓
                         Raw Text                Content Blocks
                                                   |
                                                   |
                                                   ↓
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| Final Markdown   |<----| Document Header  |<----| Markdown         |
| Document         |     | + TOC            |     | Generator        |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                                                   |
                                                   | generate_markdown()
                                                   ↓
                                               +------------------+
                                               |                  |
                                               | For each block:  |
                                               | _format_block()  |
                                               |                  |
                                               +------------------+
                                                   |
                                                   ↓
                          +---------------------------------------------+
                          |                                             |
                          ↓                 ↓                 ↓         ↓
                  +-------------+   +-------------+   +-------------+   +-------------+
                  |             |   |             |   |             |   |             |
                  | _format_    |   | _format_    |   | _format_    |   | _format_    |
                  | heading()   |   | command()   |   | code()      |   | network()   |
                  |             |   |             |   |             |   |             |
                  +-------------+   +-------------+   +-------------+   +-------------+
                          |                 |                 |                 |
                          +---------------------------------------------+
                                                   |
                                                   ↓
                                               Formatted Markdown
```


The `__init__` method initializes the generator with default formatting rules. The `setup_formatting_rules` method defines how each content type should be formatted. The `generate_markdown` method converts a list of content blocks to markdown. The `_format_block` method formats a single content block based on its type. The `_format_heading`, `_format_command`, `_format_code`, `_format_network`, `_format_path`, and `_format_url` methods format specific content types. The `_format_text
```python
# src/markdown_generator.py
from typing import List, Optional
from src.content_analyzer import ContentBlock
import re

class MarkdownGenerator:
    """
    Converts classified content blocks into properly formatted markdown.
    
    This is like a skilled translator that knows exactly how to 
    format each type of content in markdown.
    """
    
    def __init__(self):
        """Initialize the markdown generator with formatting rules."""
        self.setup_formatting_rules()
        self.setup_pattern_matches()
    
```

The `setup_formatting_rules()` method establishes the core configuration for markdown conversion by:

1. **Defining language detection rules** - Maps common commands and syntax patterns to their appropriate programming languages for proper code block formatting

2. **Setting content presentation thresholds** - Determines when to use inline code vs. full code blocks based on content length (50 characters)

3. **Establishing heading hierarchy rules** - Creates intelligent mappings between content keywords and appropriate heading levels to maintain consistent document structure

This configuration enables the markdown generator to make smart formatting decisions without requiring manual specification for each content block, resulting in consistently formatted technical documentation.

```python
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
    
```
The `generate_markdown()` method transforms a list of classified content blocks into a formatted markdown document by:

1. **Iterating through each content block** sequentially
2. **Skipping empty blocks** while preserving appropriate spacing
3. **Formatting each block** by calling the appropriate specialized method based on content type
4. **Managing spacing between blocks** based on content type transitions
5. **Tracking previous block types** to make intelligent formatting decisions
6. **Joining all formatted blocks** into a single cohesive markdown string

This method serves as the main orchestrator of the markdown generation process, delegating specific formatting tasks to specialized helper methods while maintaining the overall document structure and flow.

```python
   def setup_pattern_matches(self):
        """Define regex patterns for different content types."""
        
        # Command patterns - common HTB tools and syntax
        self.command_patterns = [
            r'^[a-zA-Z0-9_\-\.]+\s+\-[a-zA-Z0-9\-]+',  # tool with flags
            r'^(nmap|gobuster|dirb|nikto|sqlmap|hydra|john|hashcat)',  # common tools

        self.path_patterns = [
            r'^/[a-zA-Z0-9_\-\./]+$',  # Unix path only
            r'^[A-Za-z]:\\[a-zA-Z0-9_\-\\\./]+$',  # Windows path only
            r'^~/[a-zA-Z0-9_\-\./]*$',  # Home directory path only
        ]

        self.ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]+)?\b'
        
        self.url_pattern = r'(https?://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+)'

```
```
+------------------------------------------+
|        generate_markdown() method        |
+------------------------------------------+
| 1. Initialize empty markdown_lines list  |
| 2. Track previous_block_type = None     |
+------------------------------------------+
                     |
                     ↓
+------------------------------------------+
|       For each content block:            |
+------------------------------------------+
                     |
                     ↓
              +-------------+
              | Empty text? |---Yes--→ Add spacing if needed
              +-------------+           and continue to next block
                     |
                     | No
                     ↓
+------------------------------------------+
| Call _format_block() to format based     |
| on content_type                          |
+------------------------------------------+
                     |
                     ↓
+------------------------------------------+
| Check if spacing needed between blocks   |
| using _needs_spacing()                   |
+------------------------------------------+
                     |
                     ↓
+------------------------------------------+
| If spacing needed, append empty line     |
+------------------------------------------+
                     |
                     ↓
+------------------------------------------+
| Append formatted content to markdown_lines|
+------------------------------------------+
                     |
                     ↓
+------------------------------------------+
| Update previous_block_type               |
+------------------------------------------+
                     |
                     ↓
+------------------------------------------+
| Continue loop for next block             |
+------------------------------------------+
                     |
                     ↓
+------------------------------------------+
| Join all lines with newlines             |
| Return complete markdown string          |
+------------------------------------------+
```


```python
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
        
        for block in content_blocks:
            if self._handle_empty_block(block, previous_block_type, markdown_lines):
                continue
           
            # Generate markdown for this block
            markdown_content = self._format_block(block)
            
            # Add appropriate spacing
            if self._needs_spacing(previous_block_type, block.content_type):
                markdown_lines.append("")
            
            markdown_lines.append(markdown_content)
            previous_block_type = block.content_type
        
        return "\n".join(markdown_lines)
    
        def _handle_empty_block(self, block, previous_block_type, markdown_lines):
        """Handle empty blocks and add appropriate spacing."""
        if not block.text.strip():
            # Add spacing between sections
            if previous_block_type and previous_block_type != "empty":
                markdown_lines.append("")
            return True  # Indicates this was an empty block
        return False  # Not an empty block

```
The `_format_block()` method serves as a central routing mechanism that directs each content block to its appropriate specialized formatting method based on the block's content type. It:

1. **Examines the content type** of the incoming block
2. **Routes the block** to the corresponding specialized formatter:
   - Headings → `_format_heading()`
   - Commands → `_format_command()`
   - Code → `_format_code()`
   - Network info → `_format_network()`
   - Paths → `_format_path()`
   - URLs → `_format_url()`
   - Regular text → `_format_text()`

3. **Returns the formatted markdown** produced by the specialized formatter

This method implements a simple but effective control flow pattern that:
- Maintains separation of concerns by delegating specific formatting logic to specialized methods
- Creates a single point of entry for all formatting operations
- Makes the code more maintainable by organizing formatting logic by content type
- Simplifies adding support for new content types in the future

The method acts as a "traffic director" that ensures each content block is processed by the most appropriate formatting logic.

```python
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
   
```
The `_format_heading()` method transforms a heading block into markdown by:

1. **Removing common prefixes** like `#`, numbers, and periods
2. **Determining the heading level** based on content and metadata
3. **Generating the markdown heading** with the appropriate number of `#` symbols

```python
    def _format_heading(self, block: ContentBlock) -> str:
        """Format heading blocks."""
        text = block.text.strip()
        text = self._remove_common_prefixes(text)
        assert block.metadata is not None
        level = self._determine_heading_level(text, block.metadata.get("level", 2))
        return f"{'#' * level} {text}"


     def _remove_common_prefixes(self, text: str) -> str:
        """Remove common prefixes from heading text."""
        text = text.lstrip("#").strip()
        text = text.lstrip("0123456789.").strip()
        return text

     def _determine_heading_level(self, text: str, metadata_level: int = 2) -> int:
        """
        Determine the appropriate heading level based on content and metadata.
        
        Args:
            text: The heading text
            metadata_level: The level suggested by metadata (default: 2)
            
        Returns:
            int: The determined heading level (1-6)
        """
        # Start with the metadata-suggested level
        level = metadata_level
        
        # Adjust level based on content keywords
        text_lower = text.lower()
        for check_level, keywords in self.heading_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                level = check_level
                break
        
        # Ensure level is between 1 and 6
        return max(1, min(6, level))
   
```
The `_format_command()` method formats a command block into markdown by:

1. **Removing shell prompts** like `$` and `#`
2. **Detecting the command language** for proper code block formatting
3. **Choosing between inline code and code blocks** based on content length

```python
    def _format_command(self, block: ContentBlock) -> str:
        """Format command blocks."""
        text = block.text.strip()
        text = self._remove_shell_prompts(text)
        language = self._detect_command_language(text)
        if self._is_short_command(text):
            return f"`{text}`"
        
        # Use code block for longer commands
        return f"```{language}\n{text}\n```"
    
    def _remove_shell_prompts(self, text: str) -> str:
        """Remove common shell prompts from command text."""
        return text.lstrip("$#").strip()

    def _is_short_command(self, text: str) -> bool:
        """Check if the command is short enough for inline code."""
        return len(text) <= self.inline_code_max_length and "\n" not in text
```
The `_format_code()` method formats a code block into markdown by:

1. **Extracting the code language** from the block metadata
2. **Choosing between inline code and code blocks** based on content length

```python
    def _format_code(self, block: ContentBlock) -> str:
        """Format code blocks."""
        text = block.text.strip()
        language = block.metadata.get("language", "")
        if self._is_short_code(text): 
            return f"`{text}`"
        return f"```{language}\n{text}\n```"

    def _is_short_code(self, text: str) -> bool:
        """Check if the code is short enough for inline code."""
        return len(text) <= self.inline_code_max_length and "\n" not in text
    
```
The `_format_network()` method formats network-related content into markdown by:

1. **Checking if the block contains just an IP address** or a port
2. **Using inline code** for standalone IPs or ports
3. **Highlighting IPs and ports** within regular text

```python
    def _format_network(self, block: ContentBlock) -> str:
        """Format network-related content."""
        text = block.text.strip()
        
        # Check if it's just an IP or if it's part of a sentence
        if re.fullmatch(self.ip_pattern, text):
            # Just an IP address - use inline code
            return f"`{text}`"
        else:
            # IP within text - highlight the IP
            highlighted = re.sub(self.ip_pattern, r'`\g<0>`', text)
            return highlighted
    
```
**Understanding the IP Address Regex Pattern**:

The regex pattern `r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]+)?\b'` (defined in `setup_pattern_matches()`) looks complex, but we can break it down into simple parts:

## Step-by-Step Breakdown:

1. `\b` - Word boundary marker
   * Ensures we match whole IP addresses, not parts of larger words

2. `(?:[0-9]{1,3}\.){3}` - First part of an IP address
   * `[0-9]{1,3}` - A number between 1-3 digits (like 1, 42, or 192)
   * `\.` - A literal dot character
   * `{3}` - Repeat the above pattern exactly 3 times
   * `(?:...)` - Group everything together (without capturing)

3. `[0-9]{1,3}` - Last part of the IP address
   * Another 1-3 digit number

4. `(?::[0-9]+)?` - Optional port number
   * `(?:...)` - Group everything together
   * `:` - A literal colon character
   * `[0-9]+` - One or more digits (the port number)
   * `?` - Makes the entire port section optional

5. `\b` - Another word boundary marker
   * Ensures the IP address ends cleanly

## In Plain English:
This pattern matches:
- Four numbers (1-3 digits each) separated by dots
- Optionally followed by a colon and more digits (for port numbers)
- The pattern must stand alone (not be part of a larger word)

## Examples of Matches:
- `192.168.1.1`
- `10.0.0.1:8080`
- `127.0.0.1:443`

This pattern helps identify IP addresses (with optional port numbers) in text.

The `r'`\g<0>`'` expression in the `re.sub()` function is a replacement pattern that does the following:

1. **`` ` ``** - A literal backtick character (the markdown syntax for inline code)
2. **`\g<0>`** - A special regex replacement syntax that means "insert the entire matched text here"
3. **`` ` ``** - Another literal backtick character to close the inline code

In plain English, this pattern says: "Take whatever text matched my regex pattern and wrap it in backticks."

For example, if the regex pattern matches the IP address `192.168.1.1` within a longer text, the replacement will turn it into `` `192.168.1.1` ``.

The `\g<0>` syntax is particularly useful because:
- It preserves the exact text that was matched
- It works with any regex pattern without having to modify the replacement string
- It's more explicit than the simpler `\0` syntax (which does the same thing)

This is how the method highlights technical elements (like IP addresses) within regular text by wrapping them in markdown inline code formatting.

The `_format_path()` method formats file path content into markdown by:

1. **Checking if the block contains just a file path** or if it's part of a sentence
2. **Using inline code** for standalone paths
3. **Highlighting paths** within regular text

```python
    def _format_path(self, block: ContentBlock) -> str:
        """Format file path content."""
        text = block.text.strip()
        # Check if it's just a path or part of a sentence
        if self._is_path_only(text):
            return f"`{text}`"
        else:
            # Path within text - highlight paths
            highlighted = self._highlight_paths(text)  
            return highlighted

    
    def _is_path_only(self, text: str) -> bool:
        """Check if the text contains only a file path."""
        return any(re.match(pattern, text) for pattern in self.path_patterns)

    def _highlight_paths(self, text: str) -> str:
        """Highlight file paths within regular text."""
        for pattern in self.path_patterns:
            # Remove ^ and $ anchors for in-text matching
            in_text_pattern = pattern.replace('^', '').replace('$', '')
            text = re.sub(in_text_pattern, r'`\g<0>`', text)
        return text
```
The `_format_path()` method uses several regex patterns to identify and format file paths. They are defined in the `setup_pattern_matches()` method. Let's break them down:

## Pattern 1: Unix Paths
```
r'^/[a-zA-Z0-9_\-\./]+$'
```

In simple terms:
- `^/` - Must start with a forward slash
- `[a-zA-Z0-9_\-\./]+` - Contains one or more letters, numbers, underscores, hyphens, dots, or slashes
- `$` - Nothing else after the path

Examples: `/etc/passwd`, `/var/www/html`, `/home/user/documents`

## Pattern 2: Windows Paths
```
r'^[A-Za-z]:\\[a-zA-Z0-9_\-\\\./]+$'
```

In simple terms:
- `^[A-Za-z]:\\` - Must start with a letter followed by a colon and backslash
- `[a-zA-Z0-9_\-\\\./]+` - Contains one or more letters, numbers, underscores, hyphens, backslashes, dots, or slashes
- `$` - Nothing else after the path

Examples: `C:\Windows\System32`, `D:\Documents\file.txt`

## Pattern 3: Home Directory Paths
```
r'^~/[a-zA-Z0-9_\-\./]*$'
```

In simple terms:
- `^~/` - Must start with a tilde and slash (Unix shorthand for home directory)
- `[a-zA-Z0-9_\-\./]*` - Contains zero or more letters, numbers, underscores, hyphens, dots, or slashes
- `$` - Nothing else after the path

Examples: `~/Documents`, `~/projects/code.py`

## How the Method Uses These Patterns:

1. First, it checks if the text is ONLY a path (using `re.match` with the patterns above)
2. If it's just a path, it wraps the entire text in backticks: `` `path` ``
3. If the text contains paths mixed with other content, it finds all paths using similar patterns and wraps only those parts in backticks

This approach ensures paths are properly formatted whether they appear alone or within larger text blocks.

The `_format_url()` method formats URL content into markdown by:

1. **Replacing URLs** with markdown links
2. **Preserving the original text** for any non-URL content
3. **Handling multiple URLs** within a single block

It uses a nested function `make_link()` that:
- Takes each URL match from the regex pattern
- Creates a markdown link format `[url](url)` where the URL serves as both the link text and destination
- Returns the formatted link to replace the original URL

The method then uses `re.sub()` to find all URLs in the text and replace them with properly formatted markdown links, maintaining the surrounding text intact.

This approach ensures URLs are clickable in the final markdown document while preserving their readability.

```python
    def _format_url(self, block: ContentBlock) -> str:
        """Format URL content."""
        text = block.text.strip()
        
        # Replace URLs with markdown links
        def make_link(match):
            url = match.group(1)
            return f"[{url}]({url})"
        
        formatted = re.sub(self.url_pattern, make_link, text)
        return formatted
    
```
The `make_link` function is called indirectly through the `re.sub()` function. Here's how it works:

1. The `make_link` function is defined as a nested function inside `_format_url()`
2. It's passed as a callback to `re.sub()`
3. `re.sub()` searches the text for patterns matching `self.url_pattern`
4. Every time `re.sub()` finds a match, it calls `make_link()` with the match object
5. `make_link()` extracts the URL from the match and returns the formatted markdown link
6. `re.sub()` replaces the original URL with the formatted link returned by `make_link()`

This pattern (using a callback function with `re.sub()`) is a powerful way to perform complex replacements in text. Instead of just replacing with a static string, you can dynamically generate the replacement based on what was matched.

Let's clarify how `re.sub()` works with a callback function:

```python
re.sub(pattern, replacement_function, string)
```

When you use a function as the second argument to `re.sub()`:

1. The `pattern` defines what to search for in the string
2. For each match found, `re.sub()` calls `replacement_function(match_object)`
3. The `match_object` contains information about what was matched
4. The function must return a string that will replace the matched text

So the pattern is NOT passed to the function. Instead:

- The pattern is used by `re.sub()` to find matches in the text
- Each match creates a match object
- The match object is passed to your function
- Let's look at the `make_link` function in more detail:

In the `make_link` example:

```python
def make_link(match):  # match is a match object, not the pattern
    url = match.group(1)  # Extract the captured group from the match
    return f"[{url}]({url})"  # Return the replacement string
```

The function receives a match object that contains what was matched by the pattern, not the pattern itself. The function then uses `match.group(1)` to extract the first captured group from the match (in this case, the URL).

The `_format_text()` method enhances regular text content by applying markdown formatting to highlight important information. It:

1. **Cleans the input text** by removing extra whitespace
2. **Identifies important terms** from a predefined list of keywords
3. **Applies bold formatting** to these terms using markdown's `**term**` syntax
4. **Preserves the original text** otherwise

This method improves readability of technical documentation by emphasizing critical information, warnings, and important notes without changing the overall content or structure of the text.

The method uses regular expressions with word boundaries to ensure only complete words are matched, and case-insensitive matching to catch terms regardless of capitalization.


```python
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
    
```

### Line 1-2: Method Definition and Docstring
```python
def _format_text(self, block: ContentBlock) -> str:
    """Format regular text content."""
```
- Defines a method that takes a `ContentBlock` object and returns a string
- The docstring explains that this method formats regular text content

### Line 3: Text Preparation
```python
text = block.text.strip()
```
- Extracts the text from the content block
- Removes any leading or trailing whitespace with `strip()`

### Line 6: Important Terms Definition
```python
important_terms = ["important", "note", "warning", "critical", "vulnerable", "exploit"]
```
- Creates a list of words that should be emphasized in the output
- These are terms that typically indicate important information in technical documentation

### Line 7-9: Term Highlighting Loop
```python
for term in important_terms:
    pattern = rf'\b({term})\b'
    text = re.sub(pattern, r'**\1**', text, flags=re.IGNORECASE)
```
- Loops through each important term
- Creates a regex pattern that matches the term as a whole word (`\b` means word boundary)
- The parentheses in the pattern create a capture group
- Uses `re.sub()` to replace each match with the same text wrapped in `**` (markdown bold)
- The `\1` in the replacement refers to the captured group (the term itself)
- The `re.IGNORECASE` flag makes the matching case-insensitive

### Line 11: Return Formatted Text
```python
return text
```
- Returns the enhanced text with important terms now in bold markdown syntax

The `_detect_command_language()` method intelligently identifies the appropriate language for command syntax highlighting by:

1. **Analyzing command content** to look for tool-specific keywords
2. **Matching tools to languages** using a predefined mapping dictionary
3. **Defaulting to bash** when no specific language is detected

This method enables accurate syntax highlighting in the markdown output by ensuring commands are tagged with the correct language identifier, improving readability and technical accuracy of command blocks without requiring manual language specification.

```python
    def _detect_command_language(self, command: str) -> str:
        """Detect the appropriate language tag for a command."""
        command_lower = self._normalize_command(command)
        
        detected_language = self._find_matching_language(command_lower)
        if detected_language:
            return detected_language
        
        # Default to bash for unknown commands
        return "bash"

    def _normalize_command(self, command: str) -> str:
        """Normalize command for consistent matching."""
        return command.lower()

    def _find_matching_language(self, command_lower: str) -> str:
        """Find the language that matches the command based on tools."""
        for language, tools in self.language_mappings.items():
            if self._command_contains_any_tool(command_lower, tools):
                return language
        return ""

    def _command_contains_any_tool(self, command_lower: str, tools: list) -> bool:
        """Check if command contains any of the specified tools."""
        return any(tool in command_lower for tool in tools)
```
## What This Code Does:

1. It converts the command to lowercase for case-insensitive matching
2. It loops through each language and its associated tools in the `language_mappings` dictionary
3. For each language, it checks if ANY of the tools for that language appear in the command
4. If a match is found, it immediately returns that language
5. If no matches are found after checking all languages, it returns "bash" as the default

## Example:

If the command is `nmap -sV 10.10.10.1`, the method will:
1. Convert to lowercase: `nmap -sv 10.10.10.1`
2. Check if any tools in each language list appear in the command
3. Find "nmap" in the bash tools list
4. Return "bash" as the language

This ensures commands are properly syntax-highlighted in the markdown output, making the documentation more readable and technically accurate.
```
+------------------------------------------+
|        _needs_spacing() method           |
+------------------------------------------+
| Checks if spacing needed between blocks  |
| by delegating to specialized methods     |
+------------------------------------------+
                     |
          +----------+----------+
          |                     |
          v                     v
+------------------+  +------------------+
| _is_heading_     |  | _is_different_   |
| spacing_needed() |  | type_spacing_    |
|                  |  | needed()         |
+------------------+  +------------------+
```

## Example 1: Heading Spacing
```
[Previous Block]
Type: "text"
Content: "This is some text."

[Current Block]
Type: "heading"
Content: "# New Section"

_is_heading_spacing_needed() returns TRUE because:
- current_type is "heading"

Result: Empty line added between blocks
```

## Example 2: Different Type Spacing
```
[Previous Block]
Type: "command"
Content: "nmap -sV 10.10.10.1"

[Current Block]
Type: "code"
Content: "def example():"

_is_different_type_spacing_needed() returns TRUE because:
- previous_type ("command") != current_type ("code")

Result: Empty line added between blocks
```

## Example 3: Text to Network (Exception)
```
[Previous Block]
Type: "text"
Content: "The server is at"

[Current Block]
Type: "network"
Content: "192.168.1.1"

_is_different_type_spacing_needed() returns FALSE because:
- Special exception for text → network transition

Result: No empty line added (blocks flow together)
```

## Example 4: Same Type
```
[Previous Block]
Type: "command"
Content: "cd /var/www"

[Current Block]
Type: "command"
Content: "ls -la"

Both methods return FALSE because:
- Not heading-related
- Same content type

Result: No empty line added
```
The `_needs_spacing()` method and its submethods only determine *whether* spacing is needed between blocks - they don't actually add the spacing themselves.

These methods return a boolean value:
- `True` if spacing is needed
- `False` if spacing is not needed

The actual spacing (adding an empty line) is handled in the `generate_markdown()` method, which uses the result from `_needs_spacing()` to decide whether to add an empty line to the markdown output:

```python
# In generate_markdown() method
if self._needs_spacing(previous_block_type, block.content_type):
    markdown_lines.append("")  # This is where the actual spacing is added
```

This separation of concerns is good design:
1. The spacing decision logic is isolated in dedicated methods
2. The actual markdown generation (including adding spacing) is handled in the main method
3. This makes the code more maintainable and easier to test

these methods only make the decision about spacing, they don't implement the spacing themselves.


```python
    def _needs_spacing(self, previous_type: Optional[str], current_type: str) -> bool:
        """Determine if spacing is needed between content blocks."""
        
        if self._is_heading_spacing_needed(previous_type, current_type):
            return True
        
        if self._is_different_type_spacing_needed(previous_type, current_type):
            return True
        
        return False

    def _is_heading_spacing_needed(self, previous_type: Optional[str], current_type: str) -> bool:
        """Check if spacing is needed due to headings."""
        # Always add space before headings
        if current_type == "heading":
            return True
        
        # Add space after headings
        if previous_type == "heading":
            return True
        
        return False

    def _is_different_type_spacing_needed(self, previous_type: Optional[str], current_type: str) -> bool:
        """Check if spacing is needed between different content types."""
        # Add space between different content types
        if previous_type and previous_type != current_type:
            # Exception: don't add space between text and network/path/url
            if previous_type == "text" and current_type in ["network", "path", "url"]:
                return False
            return True
        
        return False
```

```python
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
    
```

```python
    def generate_table_of_contents(self, content_blocks: List[ContentBlock]) -> str:
        """Generate a table of contents from headings."""
        
        toc_lines = ["## Table of Contents", ""]
        
.        for block in content_blocks:
            if block.content_type == "heading":
                level = block.metadata.get("level", 2)
                text = block.text.strip().lstrip("#").strip()
                
                # Create anchor link
                anchor = text.lower().replace(" ", "-").replace(".", "")
                indent = "  " * (level - 1)
                
                toc_lines.append(f"{indent}- [{text}](#{anchor})")
        
        toc_linesappend("")
        return "\n".join(toc_lines)
```

## Step 2: Create a Complete Parser Test

Now let's create a test that combines all our components. Create `complete_parser_test.py`:

```python
# complete_parser_test.py
from src.pdf_processor import PDFProcessor
jrom src.content_analyzer import ContentAnalyzer
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
