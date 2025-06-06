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
    

    def setup_pattern_matches(self):
        """Define regex patterns for different content types."""
        
        # Command patterns - common HTB tools and syntax
        self.command_patterns = [
            r'^[a-zA-Z0-9_\-\.]+\s+\-[a-zA-Z0-9\-]+',  # tool with flags
            r'^(nmap|gobuster|dirb|nikto|sqlmap|hydra|john|hashcat)'  # common tools
        ]

        self.path_patterns = [
            r'^/[a-zA-Z0-9_\-\./]+$',  # Unix path only
            r'^[A-Za-z]:\\[a-zA-Z0-9_\-\\\./]+$',  # Windows path only
            r'^~/[a-zA-Z0-9_\-\./]*$',  # Home directory path only
        ]

        self.ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]+)?\b'
        
        self.url_pattern = r'(https?://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+)'


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

    def _format_code(self, block: ContentBlock) -> str:
        """Format code blocks."""
        text = block.text.strip()
        assert block.metadata is not None
        language = block.metadata.get("language", "")
        if self._is_short_code(text): 
            return f"`{text}`"
        return f"```{language}\n{text}\n```"

    def _is_short_code(self, text: str) -> bool:
        """Check if the code is short enough for inline code."""
        return len(text) <= self.inline_code_max_length and "\n" not in text
 
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

    def _format_url(self, block: ContentBlock) -> str:
        """Format URL content."""
        text = block.text.strip()
        
        # Replace URLs with markdown links
        def make_link(match):
            url = match.group(1)
            return f"[{url}]({url})"
        
        formatted = re.sub(self.url_pattern, make_link, text)
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
                assert block.metadata is not None
                level = block.metadata.get("level", 2)
                text = block.text.strip().lstrip("#").strip()
                
                # Create anchor link
                anchor = text.lower().replace(" ", "-").replace(".", "")
                indent = "  " * (level - 1)
                toc_lines.append(f"{indent}- [{text}](#{anchor})")
        
        toc_lines.append("")
        return "\n".join(toc_lines)

