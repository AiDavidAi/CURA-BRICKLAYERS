"""
BrickLayers post‑processing script for Ultimaker Cura
----------------------------------------------------

This script integrates the BrickLayers algorithm into Cura's post‑
processing framework.  When enabled, it rewrites the wall loops in the
G‑code produced by Cura (or compatible slicers) into a staggered,
hexagonal arrangement, greatly improving layer adhesion.

Version: v1.0.0-cura
Based on: GeekDetour/BrickLayers v0.2.1

Installation
============

Place this file and the accompanying `bricklayers.py` in Cura's
configuration `scripts` folder (open the folder via *Help → Show
Configuration Folder*).  Alternatively, package them as a plug‑in by
zipping them with a `plugin.json` and `__init__.py`.  The file name,
class name and key in the JSON definition must match exactly for Cura
to load the script【661191041543231†L158-L169】.  For this script the
file is named ``BrickLayersCuraScript.py``, the class is
``BrickLayersCuraScript`` and the key is ``BrickLayersCuraScript``.

Usage
=====

After installation and restarting Cura, select *Extensions →
Post Processing → Modify G‑Code*, click *Add a script* and choose
**BrickLayers**.  Configure the settings (enable, starting layer,
extrusion multiplier and layers to ignore) and slice your model.  The
algorithm uses Cura’s layer comments (`;LAYER:<n>`) to rebuild the
output file and supports Cura’s wall type names and mesh markers【256029318565517†L110-L116】【661191041543231†L158-L169】.
"""

import os
import sys
import re
from typing import List, Iterable

from ..Script import Script  # type: ignore


def _import_bricklayers() -> "module":
    """Import the bricklayers module from the same directory.

    When this script is run by Cura as a post‑processing script, the
    current working directory is the scripts folder.  To ensure that
    `bricklayers.py` located alongside this file can be imported,
    temporarily append the directory containing this script to
    ``sys.path``.  If the module is already imported, it will be
    returned directly.
    """
    module_name = "bricklayers"
    if module_name in sys.modules:
        return sys.modules[module_name]

    this_dir = os.path.dirname(os.path.realpath(__file__))
    if this_dir not in sys.path:
        sys.path.insert(0, this_dir)
    return __import__(module_name)


class BrickLayersCuraScript(Script):
    """Cura post‑processing wrapper around the BrickLayers processor.

    The `execute` method takes Cura’s internal representation of the
    G‑code (a list of layers, each of which is a list of strings),
    flattens it to a single stream, runs the BrickLayers algorithm, and
    then rebuilds the layer structure based on layer change comments.
    """

    def __init__(self) -> None:
        super().__init__()

    def getSettingDataString(self) -> str:
        """Return the JSON description of user‑adjustable settings.

        Cura expects the ``settings`` section to be a dictionary where
        each key corresponds to a setting name and the value is a
        dictionary describing that setting.  The fields used here
        (``label``, ``description``, ``type`` and ``default_value``)
        follow the structure of Cura’s built‑in post‑processing scripts
        such as PauseAtHeight【383798442649069†L20-L28】.  Using a list
        instead of a dictionary causes Cura to throw an
        ``AttributeError: 'list' object has no attribute 'items'`` at
        load time【661191041543231†L158-L169】.
        """
        import json
        # Build a dictionary describing each setting.  The keys must
        # match the setting names used in ``getSettingValueByKey``.
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
        """Run the BrickLayers algorithm and return modified G‑code.

        Parameters
        ----------
        data: A list of layers, each containing a list of G‑code lines.

        Returns
        -------
        A new list of layers with the BrickLayers transformations
        applied.  The layer boundaries are reconstructed using the
        `;LAYER:` comments emitted by the slicer.  If the user
        disables the script via the `enabled` setting, the input
        structure is returned unchanged.
        """
        enabled = self.getSettingValueByKey("enabled")
        if isinstance(enabled, str):
            enabled = enabled.lower() in ("true", "1", "yes")
        if not enabled:
            return data

        flat_lines: List[str] = [line for layer in data for line in layer]

        bl = _import_bricklayers()
        BrickLayersProcessor = bl.BrickLayersProcessor  # type: ignore

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