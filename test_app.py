#!/usr/bin/env python3
"""
Test script for UI Easy application
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from core.config import Config
        from core.image_analyzer import ImageAnalyzer
        from models.model_factory import ModelFactory
        print("✓ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration system"""
    try:
        from core.config import Config
        config = Config()
        print("✓ Configuration system initialized")
        
        # Test model config
        model_config = config.get_model_config("powerful_model")
        if model_config:
            print(f"✓ Model config loaded: {model_config.name}")
        
        # Test module config
        module_config = config.get_module_config("image_analyzer")
        if module_config:
            print("✓ Module config loaded")
        
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_image_analyzer():
    """Test image analyzer initialization"""
    try:
        from core.config import Config
        from core.image_analyzer import ImageAnalyzer
        
        config = Config()
        analyzer = ImageAnalyzer(config)
        print("✓ Image analyzer initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Image analyzer error: {e}")
        return False

def main():
    """Run all tests"""
    print("UI Easy - System Test")
    print("=" * 30)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Image Analyzer Test", test_image_analyzer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  Test failed!")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Configure API keys in config.json")
        print("2. Run 'python main.py' to start the application")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()