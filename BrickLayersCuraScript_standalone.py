"""
BrickLayers post‑processing script for Ultimaker Cura (Standalone Version)
--------------------------------------------------------------------------

This is a standalone version that can be tested outside of Cura for debugging.
It includes mock classes to simulate Cura's environment.

Version: v1.0.0-cura
Based on: GeekDetour/BrickLayers v0.2.1
"""

import os
import sys
import re
import json
from typing import List, Iterable, Any

# Mock Script class for standalone testing
class MockScript:
    """Mock version of Cura's Script class for standalone testing"""
    def __init__(self):
        self.settings = {}
    
    def getSettingValueByKey(self, key: str) -> Any:
        return self.settings.get(key, None)

# Try to import from Cura, fall back to mock if not available
try:
    from ..Script import Script  # type: ignore
except ImportError:
    # Running outside Cura, use mock
    Script = MockScript

def _import_bricklayers() -> "module":
    """Import the bricklayers module from the same directory."""
    module_name = "bricklayers"
    if module_name in sys.modules:
        return sys.modules[module_name]

    this_dir = os.path.dirname(os.path.realpath(__file__))
    if this_dir not in sys.path:
        sys.path.insert(0, this_dir)
    return __import__(module_name)

class BrickLayersCuraScript(Script):
    """Cura post‑processing wrapper around the BrickLayers processor."""

    def __init__(self) -> None:
        super().__init__()

    def getSettingDataString(self) -> str:
        """Return the JSON description of user‑adjustable settings."""
        settings_dict = {
            "enabled": {
                "label": "Enable BrickLayers",
                "description": "If disabled, the script passes G‑code through without modification.",
                "type": "bool",
                "default_value": True
            },
            "start_at_layer": {
                "label": "Start at layer",
                "description": "0‑based layer index at which BrickLayers begins moving wall loops.",
                "type": "int",
                "default_value": 3,
                "minimum_value": 0
            },
            "extrusion_multiplier": {
                "label": "Extrusion multiplier",
                "description": "Scale factor applied to the extrusion length of redistributed loops.",
                "type": "float",
                "default_value": 1.05,
                "minimum_value": 0.5,
                "maximum_value": 2.0
            },
            "layers_to_ignore": {
                "label": "Layers to ignore",
                "description": "Comma‑separated list of 0‑based layer indices where BrickLayers should be disabled.",
                "type": "str",
                "default_value": ""
            }
        }
        definition = {
            "name": "BrickLayers",
            "key": "BrickLayersCuraScript",
            "metadata": {
                "type": "postprocessing"
            },
            "version": 2,
            "settings": settings_dict
        }
        return json.dumps(definition, indent=4)

    def execute(self, data: List[List[str]]) -> List[List[str]]:
        """Run the BrickLayers algorithm and return modified G‑code."""
        
        # Check if enabled
        enabled = self.getSettingValueByKey("enabled")
        if isinstance(enabled, str):
            enabled = enabled.lower() in ("true", "1", "yes")
        if not enabled:
            return data

        # Flatten the layer structure
        flat_lines: List[str] = []
        for layer in data:
            for line in layer:
                flat_lines.append(str(line))  # Ensure string conversion

        # Import and setup BrickLayers processor
        bl = _import_bricklayers()
        BrickLayersProcessor = bl.BrickLayersProcessor  # type: ignore

        # Get settings with error handling
        try:
            start_layer = int(self.getSettingValueByKey("start_at_layer") or 0)
        except (ValueError, TypeError):
            start_layer = 0
            
        try:
            extr_mul = float(self.getSettingValueByKey("extrusion_multiplier") or 1.0)
        except (ValueError, TypeError):
            extr_mul = 1.0
            
        layers_ignore_raw = self.getSettingValueByKey("layers_to_ignore") or ""
        if isinstance(layers_ignore_raw, list):
            layers_ignore_tokens = layers_ignore_raw
        else:
            layers_ignore_tokens = re.split(r"[;,\s]+", str(layers_ignore_raw))
            
        layers_to_ignore: List[int] = []
        for token in layers_ignore_tokens:
            token = token.strip()
            if not token:
                continue
            try:
                layers_to_ignore.append(int(token))
            except ValueError:
                pass

        # Create processor
        processor = BrickLayersProcessor(
            extrusion_global_multiplier=extr_mul,
            start_at_layer=start_layer,
            layers_to_ignore=layers_to_ignore
        )

        # Process the G-code
        try:
            processed_iter: Iterable[str] = processor.process_gcode(iter(flat_lines))
            processed_lines: List[str] = []
            
            for item in processed_iter:
                # Handle different return types from the processor
                if hasattr(item, "to_gcode"):
                    gcode_result = item.to_gcode()
                    # Ensure the result is properly converted to strings
                    if isinstance(gcode_result, list):
                        for line in gcode_result:
                            processed_lines.append(str(line))
                    elif isinstance(gcode_result, str):
                        processed_lines.append(gcode_result)
                    else:
                        processed_lines.append(str(gcode_result))
                elif isinstance(item, list):
                    # If item is a list, convert each element to string
                    for line in item:
                        processed_lines.append(str(line))
                elif isinstance(item, str):
                    processed_lines.append(item)
                else:
                    # Convert any other type to string
                    processed_lines.append(str(item))
                    
        except Exception as e:
            print(f"Error during BrickLayers processing: {e}")
            # Return original data if processing fails
            return data

        # Rebuild layer structure
        boundaries = (";LAYER:", ";LAYER_CHANGE", "; CHANGE_LAYER")
        output_layers: List[List[str]] = []
        current_layer: List[str] = []
        
        for line in processed_lines:
            line_str = str(line)  # Ensure it's a string
            stripped = line_str.strip()
            
            if any(stripped.startswith(b) for b in boundaries):
                if current_layer:
                    output_layers.append(current_layer)
                    current_layer = []
                current_layer.append(line_str)
            else:
                current_layer.append(line_str)
                
        if current_layer:
            output_layers.append(current_layer)
            
        return output_layers

# For standalone testing
if __name__ == "__main__":
    print("BrickLayers Cura Script - Standalone Test")
    
    # Create test data
    test_data = [
        [";LAYER:0", "G1 X10 Y10 E1"],
        [";LAYER:1", "G1 X20 Y20 E2"],
        [";LAYER:2", "G1 X30 Y30 E3"]
    ]
    
    # Create and configure script
    script = BrickLayersCuraScript()
    script.settings = {
        "enabled": True,
        "start_at_layer": 1,
        "extrusion_multiplier": 1.05,
        "layers_to_ignore": ""
    }
    
    # Test execution
    try:
        result = script.execute(test_data)
        print(f"✅ Success: {len(result)} layers processed")
        
        # Verify all outputs are strings
        for i, layer in enumerate(result):
            for j, line in enumerate(layer):
                if not isinstance(line, str):
                    print(f"❌ Error: Layer {i}, line {j} is not a string: {type(line)}")
                    break
        else:
            print("✅ All output lines are strings")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

