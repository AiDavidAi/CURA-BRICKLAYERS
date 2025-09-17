#!/usr/bin/env python3
"""
BrickLayers Tuning Test Script
=============================

This script helps you test different BrickLayers settings to find the optimal
configuration for your prints. It generates multiple output files with
different parameter combinations.
"""

import sys
import os
from test_script import BrickLayersCuraScript

def test_parameter_combinations():
    """Test different parameter combinations"""
    print("🔧 BrickLayers Parameter Tuning Test")
    print("=" * 50)
    
    # Test configurations
    test_configs = [
        {
            "name": "Conservative",
            "start_at_layer": 5,
            "extrusion_multiplier": 1.02,
            "layers_to_ignore": ""
        },
        {
            "name": "Moderate", 
            "start_at_layer": 4,
            "extrusion_multiplier": 1.03,
            "layers_to_ignore": ""
        },
        {
            "name": "Aggressive",
            "start_at_layer": 3,
            "extrusion_multiplier": 1.05,
            "layers_to_ignore": ""
        },
        {
            "name": "Skip_Early_Layers",
            "start_at_layer": 3,
            "extrusion_multiplier": 1.05,
            "layers_to_ignore": "3,4,5"
        },
        {
            "name": "Late_Start",
            "start_at_layer": 8,
            "extrusion_multiplier": 1.05,
            "layers_to_ignore": ""
        }
    ]
    
    # Load test G-code
    input_file = "bricktest.gcode"
    if not os.path.exists(input_file):
        print(f"❌ Test file {input_file} not found")
        return False
    
    print(f"📁 Loading test file: {input_file}")
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Convert to layers (first 15 layers for comprehensive testing)
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
            if layer_count > 15:  # Test with more layers
                break
        else:
            current_layer.append(line)
    
    if current_layer:
        layers.append(current_layer)
    
    print(f"📊 Processing {len(layers)} layers with {len(test_configs)} configurations")
    
    results = []
    
    for config in test_configs:
        print(f"\n🧪 Testing configuration: {config['name']}")
        print(f"   Start layer: {config['start_at_layer']}")
        print(f"   Extrusion multiplier: {config['extrusion_multiplier']}")
        print(f"   Layers to ignore: '{config['layers_to_ignore']}'")
        
        try:
            # Create and configure script
            script = BrickLayersCuraScript()
            script.settings = {
                "enabled": True,
                "start_at_layer": config["start_at_layer"],
                "extrusion_multiplier": config["extrusion_multiplier"],
                "layers_to_ignore": config["layers_to_ignore"]
            }
            
            # Process G-code
            result = script.execute(layers)
            
            # Save output
            output_file = f"tuning_output_{config['name'].lower()}.gcode"
            with open(output_file, 'w') as f:
                for layer in result:
                    for line in layer:
                        f.write(line + "\n")
            
            # Analyze results
            total_lines = sum(len(layer) for layer in result)
            brick_lines = 0
            modified_layers = set()
            
            for i, layer in enumerate(result):
                layer_has_brick = False
                for line in layer:
                    if "BRICK:" in line:
                        brick_lines += 1
                        layer_has_brick = True
                if layer_has_brick:
                    modified_layers.add(i)
            
            analysis = {
                "config": config,
                "output_file": output_file,
                "total_lines": total_lines,
                "brick_modifications": brick_lines,
                "modified_layers": len(modified_layers),
                "first_modified_layer": min(modified_layers) if modified_layers else None
            }
            
            results.append(analysis)
            
            print(f"   ✅ Success: {brick_lines} modifications, {len(modified_layers)} layers affected")
            print(f"   💾 Saved: {output_file}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    # Print summary
    print("\n" + "=" * 50)
    print("📈 TUNING RESULTS SUMMARY")
    print("=" * 50)
    
    for result in results:
        config = result["config"]
        print(f"\n🔧 {config['name']}:")
        print(f"   Output file: {result['output_file']}")
        print(f"   BrickLayers modifications: {result['brick_modifications']}")
        print(f"   Modified layers: {result['modified_layers']}")
        print(f"   First modified layer: {result['first_modified_layer']}")
        print(f"   Settings: Start={config['start_at_layer']}, Mult={config['extrusion_multiplier']}")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Load each output file in Cura to compare the effects")
    print("2. Look for the balance between BrickLayers effect and normal walls")
    print("3. Conservative settings preserve more normal layers")
    print("4. Aggressive settings create stronger interlocking but fewer normal walls")
    print("5. Use 'Skip_Early_Layers' to preserve specific layers")
    
    return True

if __name__ == "__main__":
    success = test_parameter_combinations()
    
    if success:
        print("\n🎉 Tuning test completed successfully!")
        print("Check the generated files to find your optimal settings.")
    else:
        print("\n❌ Tuning test failed!")
        sys.exit(1)

