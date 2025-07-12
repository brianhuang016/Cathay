#!/usr/bin/env python3
"""
Test runner for Cathay mortgage calculation tests
"""

import pytest
import sys
import os

def main():
    """Run the test suite"""
    print("=== Cathay Mortgage Calculation Tests ===")
    print("Running tests for calculation result validation...")
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests with verbose output
    args = [
        "test_cathay_mortgage.py",
        "-v",
        "--tb=short",
        "--strict-markers"
    ]
    
    # Run the tests
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Some tests failed (exit code: {exit_code})")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 