# Setting Up Your Development Environment

## What We're Installing

Before we can build our parser, we need to set up our "workshop" with the right tools. Think of this like getting a toolbox ready before starting a home improvement project!

## Required Tools Overview

- **Python**: The programming language we'll use
- **Code Editor**: Where we'll write our code (VS Code recommended)
- **Git**: For version control (saving our progress)
- **Python Libraries**: Special tools for PDF processing and text analysis

## Step 1: Install Python

### Check if Python is Already Installed

First, let's see if Python is already on your computer:

**On Windows:**
1. Press `Windows + R`
2. Type `cmd` and press Enter
3. Type: `python --version`

**On Mac/Linux:**
1. Open Terminal
2. Type: `python3 --version`

If you see something like `Python 3.8.5` or higher, you're good to go! If not, let's install it.

### Installing Python

**Windows:**
1. Go to [python.org](https://python.org)
2. Click "Download Python" (get version 3.8 or newer)
3. Run the installer
4. ⚠️ **Important**: Check "Add Python to PATH" during installation

**Mac:**
1. Install Homebrew first: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Then install Python: `brew install python`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Verify Installation

Test that Python is working:
```bash
python --version
# or on Mac/Linux:
python3 --version
```

You should see: `Python 3.x.x`

## Step 2: Install a Code Editor

We recommend **Visual Studio Code** (VS Code) because it's:
- Free and easy to use
- Great for beginners
- Has helpful features for Python

### Installing VS Code

1. Go to [code.visualstudio.com](https://code.visualstudio.com)
2. Download for your operating system
3. Install with default settings

### Essential VS Code Extensions

Once VS Code is installed, add these helpful extensions:

1. **Python Extension**:
   - Open VS Code
   - Click the Extensions icon (four squares) on the left
   - Search for "Python"
   - Install the one by Microsoft

2. **Python Docstring Generator** (optional but helpful):
   - Search for "Python Docstring Generator"
   - Install it

## Step 3: Set Up Your Project Folder

### Create Project Structure

Let's create our project folder and organize it properly:

```bash
# Navigate to where you want your project
cd Desktop  # or wherever you prefer

# Create the main project folder
mkdir htb_parser
cd htb_parser

# Create subfolders
mkdir src
mkdir tests
mkdir examples
mkdir docs
```

Your folder structure should look like:
```
htb_parser/
├── src/           # Our main code files
├── tests/         # Test files
├── examples/      # Sample PDFs and outputs
├── docs/          # Documentation
└── wikis/         # These guide files
```

## Step 4: Set Up Python Virtual Environment

### What is a Virtual Environment?

Think of a virtual environment like a separate workspace for each project. It keeps all your project's tools organized and prevents conflicts between different projects.

### Creating the Virtual Environment

**Windows:**
```bash
cd htb_parser
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
cd htb_parser
python3 -m venv venv
source venv/bin/activate
```

### How to Know It's Working

When your virtual environment is active, you'll see `(venv)` at the beginning of your command prompt:
```bash
(venv) C:\Users\YourName\Desktop\htb_parser>
```

### Activating/Deactivating

**To activate** (do this every time you work on the project):
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

**To deactivate** (when you're done working):
```bash
deactivate
```

## Step 5: Install Required Python Libraries

Now let's install the tools our parser will need. Make sure your virtual environment is active!

### Create Requirements File

First, let's create a file that lists all our needed libraries:

Create a file called `requirements.txt` in your project folder:

```txt
PyMuPDF
pdfplumber
pytesseract
Pillow
spacy
click
pytest
```

### Install the Libraries

```bash
pip install -r requirements.txt
```

This might take a few minutes. You'll see lots of text scrolling by - that's normal!

### What Each Library Does

- **PyMuPDF**: Extracts text from PDF files
- **pdfplumber**: Alternative PDF processing (good for tables)
- **pytesseract**: OCR for reading text from images
- **Pillow**: Image processing
- **spacy**: Natural language processing
- **click**: Creates command-line interfaces
- **pytest**: Testing framework


**troubleshooting**


```bash
 File "/opt/homebrew/Cellar/python@3.13/3.13.3/Frameworks/Python.framework/Versions/3.13/lib/python3.13/subprocess.py", line 577, in run
   raise CalledProcessError(retcode, process.args,
                            output=stdout, stderr=stderr)
ubprocess.CalledProcessError: Command 'cd /private/var/folders/rt/250xbbk151j_1b0gmbxfjvbr0000gn/T/pip-install-gxcg4j4g/pymupdf_df0e5157597147f6ae8f0b281816fd1b/mupdf-1.23.7-source && XCFLAGS=-DTOFU_CJK_EXT /Users/ryan/htb/htb_parser/venv/bin/python3.13 ./scripts/mupdfwrap.py -d build/PyMuPDF-arm64-shared-tesseract-release -b all && echo /private/var/folders/rt/250xbbk151j_1b0gmbxfjvbr0000gn/T/pip-install-gxcg4j4g/pymupdf_df0e5157597147f6ae8f0b281816fd1b/mupdf-1.23.7-source/build/PyMuPDF-arm64-shared-tesseract-release: && ls -l /private/var/folders/rt/250xbbk151j_1b0gmbxfjvbr0000gn/T/pip-install-gxcg4j4g/pymupdf_df0e5157597147f6ae8f0b281816fd1b/mupdf-1.23.7-source/build/PyMuPDF-arm64-shared-tesseract-release' returned non-zero exit status 1.
end of output]
```
This error is showing that PyMuPDF (the `fitz` module) is failing to build during installation. The specific issue is happening during the compilation process of the MuPDF library that PyMuPDF depends on.

The error occurs because:
1. You're using Python 3.13 on a Mac with Apple Silicon (arm64)
2. The build process for PyMuPDF is failing when trying to compile the native components

To fix this issue:

1. Try installing pre-built wheels instead:
```bash
pip install --prefer-binary PyMuPDF==1.22.3
```

2. If that doesn't work, install the build dependencies first:
```bash
brew install swig freetype
```

3. Then try installing PyMuPDF again:
```bash
pip install PyMuPDF==1.22.3
```

4. If you're still having issues, you can try using a slightly older version that has better compatibility with Python 3.13:
```bash
pip install PyMuPDF==1.22.3
```

The error is common when installing packages with C extensions on newer Python versions or different architectures like Apple Silicon.


## Step 6: Install Additional Tools

### Tesseract OCR

For reading text from images in PDFs:

**Windows:**
1. Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install with default settings
3. Add to PATH if not done automatically

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

### Verify Tesseract Installation

```bash
tesseract --version
```

## Step 7: Test Your Setup

Let's make sure everything is working! Create a simple test file:

Create `test_setup.py` in your project folder:

```python
# test_setup.py
import sys
print(f"Python version: {sys.version}")

try:
    import fitz  # PyMuPDF
    print("✅ PyMuPDF installed successfully")
except ImportError:
    print("❌ PyMuPDF not found")

try:
    import pdfplumber
    print("✅ pdfplumber installed successfully")
except ImportError:
    print("❌ pdfplumber not found")

try:
    import pytesseract
    print("✅ pytesseract installed successfully")
except ImportError:
    print("❌ pytesseract not found")

print("🎉 Setup test complete!")
```

Run the test:
```bash
python test_setup.py
```

You should see all green checkmarks!

## Step 8: Configure VS Code for Your Project

### Open Your Project in VS Code

1. Open VS Code
2. File → Open Folder
3. Select your `htb_parser` folder

### Select Python Interpreter

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Choose the one in your `venv` folder

## Troubleshooting Common Issues

### "Python not found" Error

**Solution**: Make sure Python is added to your PATH during installation

### "pip not found" Error

**Solution**: 
```bash
python -m ensurepip --upgrade
```

### Virtual Environment Not Activating

**Solution**: Make sure you're in the right folder and using the correct command for your operating system

### Library Installation Fails

**Solution**: Try upgrading pip first:
```bash
python -m pip install --upgrade pip
```

## What's Next?

Congratulations! Your development environment is ready. 🎉

You now have:
- ✅ Python installed and working
- ✅ VS Code set up with Python support
- ✅ Virtual environment created
- ✅ All required libraries installed
- ✅ Project structure organized

In the next guide, we'll start building the actual parser by creating our first component: the PDF text extractor!

---

[← Previous: Understanding the Architecture](02-understanding-the-architecture.md) | [Next: Phase 1 - Basic PDF Extraction →](04-phase1-basic-pdf-extraction.md)
