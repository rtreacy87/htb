# test_content_analysis.py
from src.content_analyzer import ContentAnalyzer

def test_content_classification():
    """Test our content classification system."""
    
    # Create analyzer
    analyzer = ContentAnalyzer()
    
    # Test samples representing different content types
    test_samples = [
        "# Reconnaissance",
        "nmap -sV 10.10.10.1", "The target machine is running SSH on port 22.",
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
