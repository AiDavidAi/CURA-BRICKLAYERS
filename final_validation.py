#!/usr/bin/env python3
"""
Final validation test for BrickLayers Cura integration
"""

import os
import sys
import json
from test_script import BrickLayersCuraScript

def validate_settings():
    """Validate that settings are properly configured"""
    print("🔧 Validating settings configuration...")
    
    script = BrickLayersCuraScript()
    settings_json = script.getSettingDataString()
    
    try:
        settings = json.loads(settings_json)
        required_keys = ["name", "key", "metadata", "version", "settings"]
        
        for key in required_keys:
            if key not in settings:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Check individual settings
        setting_names = ["enabled", "start_at_layer", "extrusion_multiplier", "layers_to_ignore"]
        for setting in setting_names:
            if setting not in settings["settings"]:
                print(f"❌ Missing setting: {setting}")
                return False
        
        print("✅ Settings configuration is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in settings: {e}")
        return False

def validate_processing():
    """Validate G-code processing functionality"""
    print("🔄 Validating G-code processing...")
    
    # Test with various G-code patterns
    test_cases = [
        # Simple case
        [
            [";LAYER:0"],
            ["G1 X10 Y10 E1"],
            [";LAYER:1"],
            ["G1 X20 Y20 E2"]
        ],
        # With type markers
        [
            [";LAYER:0"],
            [";TYPE:WALL-OUTER"],
            ["G1 X10 Y10 E1"],
            [";TYPE:WALL-INNER"],
            ["G1 X15 Y15 E1.5"],
            [";LAYER:1"],
            ["G1 X20 Y20 E2"]
        ]
    ]
    
    script = BrickLayersCuraScript()
    script.settings = {
        "enabled": True,
        "start_at_layer": 0,
        "extrusion_multiplier": 1.05,
        "layers_to_ignore": ""
    }
    
    for i, test_case in enumerate(test_cases):
        try:
            result = script.execute(test_case)
            if not result or len(result) == 0:
                print(f"❌ Test case {i+1} returned empty result")
                return False
            print(f"✅ Test case {i+1} processed successfully")
        except Exception as e:
            print(f"❌ Test case {i+1} failed: {e}")
            return False
    
    return True

def validate_file_structure():
    """Validate that all required files are present"""
    print("📁 Validating file structure...")
    
    required_files = [
        "BrickLayersCuraScript.py",
        "bricklayers.py",
        "README.md"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            return False
        
        # Check file size
        size = os.path.getsize(file)
        if size == 0:
            print(f"❌ File is empty: {file}")
            return False
        
        print(f"✅ {file} exists ({size} bytes)")
    
    return True

def validate_imports():
    """Validate that all imports work correctly"""
    print("📦 Validating imports...")
    
    try:
        import bricklayers
        if not hasattr(bricklayers, 'BrickLayersProcessor'):
            print("❌ BrickLayersProcessor not found in bricklayers module")
            return False
        print("✅ bricklayers module imports correctly")
        
        from test_script import BrickLayersCuraScript
        script = BrickLayersCuraScript()
        print("✅ BrickLayersCuraScript imports correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 BrickLayers Cura Final Validation")
    print("=" * 50)
    
    tests = [
        ("File Structure", validate_file_structure),
        ("Imports", validate_imports),
        ("Settings", validate_settings),
        ("Processing", validate_processing)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY:")
    
    all_passed = all(results)
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("The BrickLayers Cura integration is ready for deployment!")
    else:
        print("⚠️  SOME VALIDATIONS FAILED!")
        print("Please fix the issues before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()

