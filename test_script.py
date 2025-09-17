#!/usr/bin/env python3
"""
Standalone test version of BrickLayers Cura integration
"""

import os
import sys
import re
import json
from typing import List, Iterable

# Mock Script class for testing
class Script:
    def __init__(self):
        self.settings = {}
    
    def getSettingValueByKey(self, key):
        return self.settings.get(key)

def _import_bricklayers():
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
        enabled = self.getSettingValueByKey("enabled")
        if isinstance(enabled, str):
            enabled = enabled.lower() in ("true", "1", "yes")
        if not enabled:
            return data

        flat_lines: List[str] = [line for layer in data for line in layer]

        bl = _import_bricklayers()
        BrickLayersProcessor = bl.BrickLayersProcessor

        try:
            start_layer = int(self.getSettingValueByKey("start_at_layer"))
        except Exception:
            start_layer = 0
        try:
            extr_mul = float(self.getSettingValueByKey("extrusion_multiplier"))
        except Exception:
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

        processor = BrickLayersProcessor(
            extrusion_global_multiplier=extr_mul,
            start_at_layer=start_layer,
            layers_to_ignore=layers_to_ignore
        )

        processed_iter: Iterable[str] = processor.process_gcode(iter(flat_lines))
        processed_lines: List[str] = []
        for item in processed_iter:
            if hasattr(item, "to_gcode"):
                processed_lines.append(item.to_gcode())
            else:
                processed_lines.append(str(item))

        boundaries = (";LAYER:", ";LAYER_CHANGE", "; CHANGE_LAYER")
        output_layers: List[List[str]] = []
        current_layer: List[str] = []
        for line in processed_lines:
            stripped = line.strip()
            if any(stripped.startswith(b) for b in boundaries):
                if current_layer:
                    output_layers.append(current_layer)
                    current_layer = []
                current_layer.append(line)
            else:
                current_layer.append(line)
        if current_layer:
            output_layers.append(current_layer)
        return output_layers

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
    
    # Set the settings
    script.settings = {
        "enabled": True,
        "start_at_layer": 1,
        "extrusion_multiplier": 1.05,
        "layers_to_ignore": ""
    }
    
    try:
        result = script.execute(simple_gcode)
        print(f"Processing successful! Input layers: {len(simple_gcode)}, Output layers: {len(result)}")
        return True
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("BrickLayers Cura Integration Test")
    print("=" * 40)
    
    success = test_basic_functionality()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Basic test passed!")
    else:
        print("❌ Test failed!")
        sys.exit(1)

