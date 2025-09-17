#!/usr/bin/env python3
"""
Comprehensive test of BrickLayers Cura integration with real G-code
"""

import os
import sys
from test_script import BrickLayersCuraScript

def test_with_real_gcode():
    """Test with the actual bricktest.gcode file"""
    print("Testing with real G-code file...")
    
    if not os.path.exists("bricktest.gcode"):
        print("bricktest.gcode not found, skipping real file test")
        return False
    
    try:
        # Read the G-code file
        with open("bricktest.gcode", "r") as f:
            lines = f.readlines()
        
        print(f"Loaded G-code file with {len(lines)} lines")
        
        # Convert to Cura's layer format
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
                if layer_count > 10:  # Test with first 10 layers for speed
                    break
            else:
                current_layer.append(line)
        
        if current_layer:
            layers.append(current_layer)
        
        print(f"Converted to {len(layers)} layers for testing")
        
        # Create script and test
        script = BrickLayersCuraScript()
        script.settings = {
            "enabled": True,
            "start_at_layer": 3,
            "extrusion_multiplier": 1.05,
            "layers_to_ignore": ""
        }
        
        print("Processing G-code with BrickLayers...")
        result = script.execute(layers)
        print(f"Real G-code processing successful! Output layers: {len(result)}")
        
        # Save result for inspection
        with open("test_output.gcode", "w") as f:
            for layer in result:
                for line in layer:
                    f.write(line + "\n")
        
        print("Output saved to test_output.gcode")
        
        # Analyze the output
        total_lines = sum(len(layer) for layer in result)
        print(f"Total output lines: {total_lines}")
        
        # Check for BrickLayers modifications
        brick_modifications = 0
        for layer in result:
            for line in layer:
                if "BrickLayers" in line or "brick" in line.lower():
                    brick_modifications += 1
        
        print(f"Lines with BrickLayers modifications: {brick_modifications}")
        
        return True
        
    except Exception as e:
        print(f"Error processing real G-code: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_gcode_structure():
    """Analyze the structure of the test G-code file"""
    print("\nAnalyzing G-code structure...")
    
    if not os.path.exists("bricktest.gcode"):
        print("bricktest.gcode not found")
        return False
    
    try:
        with open("bricktest.gcode", "r") as f:
            lines = f.readlines()
        
        layer_markers = []
        type_markers = []
        feature_types = set()
        
        for i, line in enumerate(lines[:1000]):  # Analyze first 1000 lines
            line = line.strip()
            if line.startswith(";LAYER:"):
                layer_markers.append((i, line))
            elif line.startswith(";TYPE:"):
                type_markers.append((i, line))
                feature_types.add(line)
        
        print(f"Found {len(layer_markers)} layer markers in first 1000 lines")
        print(f"Found {len(type_markers)} type markers")
        print("Feature types found:")
        for ft in sorted(feature_types):
            print(f"  {ft}")
        
        return True
        
    except Exception as e:
        print(f"Error analyzing G-code: {e}")
        return False

if __name__ == "__main__":
    print("Comprehensive BrickLayers Cura Test")
    print("=" * 50)
    
    success1 = analyze_gcode_structure()
    success2 = test_with_real_gcode()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All comprehensive tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

