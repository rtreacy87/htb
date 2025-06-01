# src/content_analyzer.py
import re
from typing import Dict, List,  Optional
from dataclasses import dataclass

@dataclass
class ContentBlock:
    """Represents a classified block of content."""
    text: str
    content_type: str
    confidence: float
    metadata: Optional[Dict] = None    

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
            r'^#\!s+',   # root prompt
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
            r'\bport\s+[0-9]+\b',  # Port references
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
            r'^#+\s+[A-Za-z0-9]',  # Markdown headings (# Title)
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

         # Check for URLs
        url_result = self._check_url(line)
        if url_result:
            return url_result       

        # Check for network elements
        network_result = self._check_network(line)
        if network_result:
            return network_result
        
        # Check for file paths
        path_result = self._check_path(line)
        if path_result:
            return path_result
        
        # Default to regular text
        return ContentBlock(line, "text", 0.8)

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

