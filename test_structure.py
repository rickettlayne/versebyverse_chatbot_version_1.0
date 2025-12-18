#!/usr/bin/env python3
"""
Test script to validate the application structure
"""
import os
import ast

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    """Test the application structure"""
    print("Testing Verse by Verse RAG Chatbot Structure")
    print("=" * 60)
    
    # List of files to check
    files_to_check = [
        'main.py',
        'src/__init__.py',
        'src/scraper/__init__.py',
        'src/scraper/pdf_scraper.py',
        'src/processor/__init__.py',
        'src/processor/pdf_processor.py',
        'src/rag/__init__.py',
        'src/rag/vector_store.py',
        'src/rag/qa_chain.py',
        'src/utils/__init__.py',
        'src/utils/config.py',
    ]
    
    all_valid = True
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            valid, error = check_file_syntax(filepath)
            if valid:
                print(f"✓ {filepath} - Valid syntax")
            else:
                print(f"✗ {filepath} - Syntax error: {error}")
                all_valid = False
        else:
            print(f"✗ {filepath} - File not found")
            all_valid = False
    
    print("\n" + "=" * 60)
    
    # Check required files
    required_files = [
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md'
    ]
    
    print("\nChecking required files:")
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath} exists")
        else:
            print(f"✗ {filepath} missing")
            all_valid = False
    
    print("\n" + "=" * 60)
    
    if all_valid:
        print("\n✓ All structure checks passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file with your OPENAI_API_KEY")
        print("3. Run the application: python main.py")
    else:
        print("\n✗ Some checks failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
