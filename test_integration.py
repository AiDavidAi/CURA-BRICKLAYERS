#!/usr/bin/env python3
"""
Test script for BrickLayers Cura integration
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the Cura Script class since we're testing outside of Cura
class MockScript:
    def __init__(self):
        self.settings = {
            "enabled": True,
            "start_at_layer": 3,
            "extrusion_multiplier": 1.05,
            "layers_to_ignore": ""
        }
    
    def getSettingValueByKey(self, key):
        return self.settings.get(key)

# Import our script
from BrickLayersCuraScript import BrickLayersCuraScript

def test_basic_functionality():
    """Test basic functionality of the BrickLayers Cura script"""
    print("Testing BrickLayers Cura Integration...")
    
    # Create script instance
    script = BrickLayersCuraScript()
    
    # Test settings
    print("Testing settings configuration...")
    settings_json = script.getSettingDataString()
    print(f"Settings JSON length: {len(settings_json)} characters")
    
    # Test with simple G-code
    print("Testing with simple G-code...")
    simple_gcode = [
        [";LAYER:0"],
        ["G1 X10 Y10 E1"],
        [";LAYER:1"],
        ["G1 X20 Y20 E2"],
        [";LAYER:2"],
        ["G1 X30 Y30 E3"]
    ]
    
    # Mock the settings
    script.getSettingValueByKey = lambda key: {
        "enabled": True,
        "start_at_layer": 1,
        "extrusion_multiplier": 1.05,
        "layers_to_ignore": ""
    }.get(key)
    
    try:
        result = script.execute(simple_gcode)
        print(f"Processing successful! Input layers: {len(simple_gcode)}, Output layers: {len(result)}")
        return True
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_real_gcode():
    """Test with the actual bricktest.gcode file"""
    print("\nTesting with real G-code file...")
    
    if not os.path.exists("bricktest.gcode"):
        print("bricktest.gcode not found, skipping real file test")
        return True
    
    try:
        # Read the G-code file
        with open("bricktest.gcode", "r") as f:
            lines = f.readlines()
        
        print(f"Loaded G-code file with {len(lines)} lines")
        
        # Convert to Cura's layer format (simplified)
        layers = []
        current_layer = []
        
        for line in lines[:1000]:  # Test with first 1000 lines for speed
            line = line.strip()
            if line.startswith(";LAYER:"):
                if current_layer:
                    layers.append(current_layer)
                current_layer = [line]
            else:
                current_layer.append(line)
        
        if current_layer:
            layers.append(current_layer)
        
        print(f"Converted to {len(layers)} layers")
        
        # Create script and test
        script = BrickLayersCuraScript()
        script.getSettingValueByKey = lambda key: {
            "enabled": True,
            "start_at_layer": 3,
            "extrusion_multiplier": 1.05,
            "layers_to_ignore": ""
        }.get(key)
        
        result = script.execute(layers)
        print(f"Real G-code processing successful! Output layers: {len(result)}")
        
        # Save result for inspection
        with open("test_output.gcode", "w") as f:
            for layer in result:
                for line in layer:
                    f.write(line + "\n")
        
        print("Output saved to test_output.gcode")
        return True
        
    except Exception as e:
        print(f"Error processing real G-code: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("BrickLayers Cura Integration Test")
    print("=" * 40)
    
    success1 = test_basic_functionality()
    success2 = test_with_real_gcode()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

