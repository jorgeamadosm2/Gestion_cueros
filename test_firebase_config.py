#!/usr/bin/env python3
"""
Test script to verify Firebase credential loading logic
"""
import json
import os
from pathlib import Path

def test_firebase_credentials():
    """Test the different methods of loading Firebase credentials"""
    
    print("🧪 Testing Firebase Credential Loading Logic\n")
    
    # Setup paths
    FIREBASE_CREDS = Path(__file__).resolve().parent / "firebase_config.json"
    
    # Test 1: Check if firebase_config.json exists
    print("Test 1: Checking firebase_config.json file")
    if FIREBASE_CREDS.exists():
        try:
            with open(FIREBASE_CREDS, 'r') as f:
                config = json.load(f)
            print(f"  ✅ firebase_config.json found and valid")
            print(f"  📋 Project ID: {config.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Error reading firebase_config.json: {str(e)}")
    else:
        print(f"  ⚠️  firebase_config.json not found (this is expected)")
    
    print()
    
    # Test 2: Check for environment variables
    print("Test 2: Checking environment variables")
    if os.getenv('FIREBASE_PROJECT_ID'):
        print(f"  ✅ Environment variables found")
        print(f"  📋 Project ID: {os.getenv('FIREBASE_PROJECT_ID')}")
    else:
        print(f"  ⚠️  FIREBASE_PROJECT_ID not set (this is expected)")
    
    print()
    
    # Test 3: Check example files exist
    print("Test 3: Checking example configuration files")
    
    example_json = Path(__file__).resolve().parent / "firebase_config_example.json"
    if example_json.exists():
        print(f"  ✅ firebase_config_example.json exists")
    else:
        print(f"  ❌ firebase_config_example.json missing")
    
    example_secrets = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml.example"
    if example_secrets.exists():
        print(f"  ✅ .streamlit/secrets.toml.example exists")
    else:
        print(f"  ❌ .streamlit/secrets.toml.example missing")
    
    print()
    
    # Test 4: Verify gitignore
    print("Test 4: Checking .gitignore configuration")
    gitignore_path = Path(__file__).resolve().parent / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        checks = {
            'firebase_config.json': 'firebase_config.json' in gitignore_content,
            '.streamlit/secrets.toml': '.streamlit/secrets.toml' in gitignore_content or 'secrets.toml' in gitignore_content,
        }
        
        for item, found in checks.items():
            if found:
                print(f"  ✅ {item} is in .gitignore")
            else:
                print(f"  ⚠️  {item} might not be in .gitignore")
    else:
        print(f"  ❌ .gitignore not found")
    
    print()
    print("=" * 60)
    print("📊 Summary:")
    print("  The app now supports three methods for Firebase credentials:")
    print("  1. firebase_config.json (local development)")
    print("  2. .streamlit/secrets.toml (Streamlit Cloud deployment)")
    print("  3. Environment variables (flexible deployment)")
    print()
    print("  See CONFIGURACION_FIREBASE.md for detailed setup instructions")
    print("=" * 60)

if __name__ == '__main__':
    test_firebase_credentials()
