#!/usr/bin/env python3
"""
Python Environment Diagnostic
Run this to check your Python setup
"""

import sys
import subprocess

print("🔍 Python Environment Diagnostic")
print("=" * 50)

# Check Python version and path
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path[:3]}...")  # First 3 paths

print("\n📦 Checking package installations:")

# Check if packages are installed
packages = ['fastapi', 'uvicorn']

for package in packages:
    try:
        __import__(package)
        print(f"✅ {package} - FOUND")
    except ImportError:
        print(f"❌ {package} - NOT FOUND")

print("\n🔍 Pip information:")
try:
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                          capture_output=True, text=True)
    lines = result.stdout.split('\n')
    for line in lines:
        if 'fastapi' in line.lower() or 'uvicorn' in line.lower():
            print(f"📋 {line}")
except Exception as e:
    print(f"❌ Error checking pip: {e}")

print("\n💡 Recommended fixes:")
print("1. Try: python -m pip install fastapi uvicorn")
print("2. Or try: python3 -m pip install fastapi uvicorn") 
print("3. Check if using virtual environment")
print("4. Try: pip install --user fastapi uvicorn")