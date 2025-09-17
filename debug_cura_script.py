#!/usr/bin/env python3
"""
BrickLayers Cura Script Debugger
================================

This script allows you to debug the BrickLayers Cura integration outside of Cura
using VSCode or any Python environment. It simulates Cura's behavior and helps
identify exactly where errors occur.

Usage:
    python debug_cura_script.py [gcode_file]

If no file is specified, it will use the test G-code files in the directory.
"""

import sys
import os
import traceback
import json
from typing import List, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_cura_environment():
    """Simulate Cura's environment and imports"""
    print("🔧 Setting up simulated Cura environment...")
    
    # Create a mock Script class to simulate Cura's Script
    class MockScript:
        def __init__(self):
            self.settings = {}
        
        def getSettingValueByKey(self, key: str) -> Any:
            return self.settings.get(key, None)
    
    # Create the mock module structure that Cura expects
    class MockScriptModule:
        Script = MockScript
    
    # Add to sys.modules to simulate Cura's import structure
    sys.modules['..Script'] = MockScriptModule
    sys.modules['Script'] = MockScriptModule
    
    print("✅ Mock Cura environment created")

def load_test_gcode(filename: str = None) -> List[List[str]]:
    """Load and parse G-code file into Cura's layer format"""
    
    # Try different test files
    test_files = [
        filename,
        "bricktest.gcode",
        "sample_gcode/Sample_3DBenchy_5walls_classic.gcode",
        "test_output.gcode"
    ]
    
    gcode_file = None
    for test_file in test_files:
        if test_file and os.path.exists(test_file):
            gcode_file = test_file
            break
    
    if not gcode_file:
        print("❌ No G-code file found. Creating minimal test data...")
        return create_minimal_test_data()
    
    print(f"📁 Loading G-code file: {gcode_file}")
    
    try:
        with open(gcode_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📊 Loaded {len(lines)} lines")
        
        # Parse into Cura's layer format
        layers = []
        current_layer = []
        layer_count = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith(";LAYER:"):
                if current_layer:
                    layers.append(current_layer)
                current_layer = [line]
                layer_count += 1
                if layer_count > 10:  # Limit for debugging
                    break
            else:
                current_layer.append(line)
        
        if current_layer:
            layers.append(current_layer)
        
        print(f"✅ Parsed into {len(layers)} layers")
        return layers
        
    except Exception as e:
        print(f"❌ Error loading G-code: {e}")
        return create_minimal_test_data()

def create_minimal_test_data() -> List[List[str]]:
    """Create minimal test data for debugging"""
    return [
        [";LAYER:0", "G1 X10 Y10 E1", "G1 X20 Y10 E2"],
        [";LAYER:1", "G1 X10 Y20 E3", "G1 X20 Y20 E4"],
        [";LAYER:2", "G1 X10 Y30 E5", "G1 X20 Y30 E6"]
    ]

def debug_import_process():
    """Debug the import process step by step"""
    print("\n🔍 DEBUGGING IMPORT PROCESS")
    print("=" * 50)
    
    try:
        print("1. Testing bricklayers module import...")
        import bricklayers
        print("   ✅ bricklayers module imported successfully")
        
        print("2. Testing BrickLayersProcessor class...")
        processor_class = getattr(bricklayers, 'BrickLayersProcessor', None)
        if processor_class:
            print("   ✅ BrickLayersProcessor class found")
        else:
            print("   ❌ BrickLayersProcessor class not found")
            return False
        
        print("3. Testing processor instantiation...")
        processor = processor_class()
        print("   ✅ BrickLayersProcessor instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        traceback.print_exc()
        return False

def debug_script_creation():
    """Debug the script creation process"""
    print("\n🔍 DEBUGGING SCRIPT CREATION")
    print("=" * 50)
    
    try:
        print("1. Importing BrickLayersCuraScript...")
        # Import the fixed version
        from BrickLayersCuraScript import BrickLayersCuraScript
        print("   ✅ BrickLayersCuraScript imported successfully")
        
        print("2. Creating script instance...")
        script = BrickLayersCuraScript()
        print("   ✅ Script instance created successfully")
        
        print("3. Testing getSettingDataString...")
        settings_json = script.getSettingDataString()
        settings_data = json.loads(settings_json)
        print(f"   ✅ Settings JSON valid: {len(settings_data)} keys")
        
        return script
        
    except Exception as e:
        print(f"   ❌ Script creation error: {e}")
        traceback.print_exc()
        
        # Try the standalone version as fallback
        try:
            print("   🔄 Trying standalone version...")
            from BrickLayersCuraScript_standalone import BrickLayersCuraScript
            script = BrickLayersCuraScript()
            print("   ✅ Standalone version works!")
            return script
        except Exception as e2:
            print(f"   ❌ Standalone version also failed: {e2}")
            return None

def debug_data_processing(script, test_data: List[List[str]]):
    """Debug the data processing step by step"""
    print("\n🔍 DEBUGGING DATA PROCESSING")
    print("=" * 50)
    
    try:
        print("1. Setting up script configuration...")
        script.settings = {
            "enabled": True,
            "start_at_layer": 2,
            "extrusion_multiplier": 1.05,
            "layers_to_ignore": ""
        }
        print("   ✅ Script configured")
        
        print("2. Analyzing input data structure...")
        print(f"   Input type: {type(test_data)}")
        print(f"   Number of layers: {len(test_data)}")
        for i, layer in enumerate(test_data[:3]):  # Show first 3 layers
            print(f"   Layer {i}: {len(layer)} lines, type: {type(layer)}")
            for j, line in enumerate(layer[:2]):  # Show first 2 lines
                print(f"     Line {j}: '{line}' (type: {type(line)})")
        
        print("3. Calling execute method...")
        result = script.execute(test_data)
        print("   ✅ Execute method completed")
        
        print("4. Analyzing output data structure...")
        print(f"   Output type: {type(result)}")
        print(f"   Number of output layers: {len(result)}")
        
        # Check each layer and line type
        for i, layer in enumerate(result[:3]):  # Check first 3 layers
            print(f"   Output Layer {i}: {len(layer)} lines, type: {type(layer)}")
            for j, line in enumerate(layer[:2]):  # Check first 2 lines
                print(f"     Line {j}: '{line}' (type: {type(line)})")
                if not isinstance(line, str):
                    print(f"     ❌ ERROR: Line is not a string! Type: {type(line)}")
                    print(f"     Content: {repr(line)}")
                    return False
        
        print("   ✅ All output lines are strings")
        return result
        
    except Exception as e:
        print(f"   ❌ Processing error: {e}")
        traceback.print_exc()
        return None

def debug_file_writing(result_data: List[List[str]]):
    """Debug the file writing process"""
    print("\n🔍 DEBUGGING FILE WRITING")
    print("=" * 50)
    
    try:
        output_file = "debug_output.gcode"
        print(f"1. Writing to file: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for layer_idx, layer in enumerate(result_data):
                print(f"   Writing layer {layer_idx} ({len(layer)} lines)...")
                for line_idx, line in enumerate(layer):
                    if not isinstance(line, str):
                        print(f"   ❌ ERROR at layer {layer_idx}, line {line_idx}")
                        print(f"      Expected str, got {type(line)}: {repr(line)}")
                        return False
                    f.write(line + "\n")
        
        print(f"   ✅ File written successfully: {output_file}")
        
        # Verify file contents
        with open(output_file, 'r', encoding='utf-8') as f:
            written_lines = f.readlines()
        
        print(f"   ✅ Verification: {len(written_lines)} lines written")
        return True
        
    except Exception as e:
        print(f"   ❌ File writing error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debugging function"""
    print("🚀 BrickLayers Cura Script Debugger")
    print("=" * 50)
    
    # Get input file from command line
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Step 1: Setup environment
    simulate_cura_environment()
    
    # Step 2: Debug imports
    if not debug_import_process():
        print("\n❌ FAILED: Import process failed")
        return False
    
    # Step 3: Debug script creation
    script = debug_script_creation()
    if not script:
        print("\n❌ FAILED: Script creation failed")
        return False
    
    # Step 4: Load test data
    test_data = load_test_gcode(input_file)
    if not test_data:
        print("\n❌ FAILED: Could not load test data")
        return False
    
    # Step 5: Debug processing
    result = debug_data_processing(script, test_data)
    if result is None:
        print("\n❌ FAILED: Data processing failed")
        return False
    
    # Step 6: Debug file writing
    if not debug_file_writing(result):
        print("\n❌ FAILED: File writing failed")
        return False
    
    print("\n🎉 SUCCESS: All debugging steps completed!")
    print("\nNext steps:")
    print("1. Check debug_output.gcode for the processed result")
    print("2. If this works, the issue might be Cura-specific")
    print("3. Try updating the files in Cura's scripts folder")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Debugging interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)

