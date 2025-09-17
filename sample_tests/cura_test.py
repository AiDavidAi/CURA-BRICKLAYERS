#!/usr/bin/env python3
"""
BrickLayers Cura Integration Test Script
========================================

This script demonstrates how to test the BrickLayers Cura integration
outside of the Cura environment for development and debugging purposes.

Usage:
    python3 cura_test.py [input_gcode_file]

If no input file is specified, it will use the sample G-code files
in the sample_gcode directory.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_cura_integration():
    """Test the BrickLayers Cura integration"""
    print("🚀 BrickLayers Cura Integration Test")
    print("=" * 50)
    
    try:
        # Import the test script from parent directory
        from test_script import BrickLayersCuraScript
        print("✅ Successfully imported BrickLayersCuraScript")
    except ImportError as e:
        print(f"❌ Failed to import BrickLayersCuraScript: {e}")
        return False
    
    # Test with sample G-code if available
    sample_files = [
        "../sample_gcode/Sample_3DBenchy_5walls_classic.gcode",
        "../sample_gcode/Sample_BrickLayersChallengeSimple_5walls.gcode",
        "bricktest.gcode"
    ]
    
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            print(f"\n📁 Testing with: {sample_file}")
            
            try:
                # Read the sample file
                with open(sample_file, 'r') as f:
                    lines = f.readlines()
                
                print(f"📊 Loaded {len(lines)} lines")
                
                # Convert to Cura layer format (first 5 layers for speed)
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
                        if layer_count > 5:  # Test with first 5 layers
                            break
                    else:
                        current_layer.append(line)
                
                if current_layer:
                    layers.append(current_layer)
                
                print(f"🔄 Processing {len(layers)} layers...")
                
                # Create and configure script
                script = BrickLayersCuraScript()
                script.settings = {
                    "enabled": True,
                    "start_at_layer": 2,
                    "extrusion_multiplier": 1.05,
                    "layers_to_ignore": ""
                }
                
                # Process the G-code
                start_time = time.time()
                result = script.execute(layers)
                end_time = time.time()
                
                print(f"✅ Processing completed in {end_time - start_time:.2f} seconds")
                print(f"📤 Output: {len(result)} layers")
                
                # Save result
                output_file = f"test_output_{os.path.basename(sample_file)}"
                with open(output_file, 'w') as f:
                    for layer in result:
                        for line in layer:
                            f.write(line + "\n")
                
                print(f"💾 Saved output to: {output_file}")
                
                # Analyze modifications
                total_lines = sum(len(layer) for layer in result)
                brick_lines = 0
                for layer in result:
                    for line in layer:
                        if "BRICK:" in line or "brick" in line.lower():
                            brick_lines += 1
                
                print(f"📈 Analysis:")
                print(f"   Total output lines: {total_lines}")
                print(f"   BrickLayers modifications: {brick_lines}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error processing {sample_file}: {e}")
                continue
    
    print("⚠️  No suitable sample files found for testing")
    return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            sys.exit(1)
        print(f"📁 Using input file: {input_file}")
    
    success = test_cura_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Install the script in Cura's scripts folder")
        print("   2. Restart Cura")
        print("   3. Enable BrickLayers in Post Processing")
        print("   4. Slice and print!")
    else:
        print("❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

