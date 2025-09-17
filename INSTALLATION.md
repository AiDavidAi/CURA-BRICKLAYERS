# BrickLayers for Cura - Installation Guide

## Quick Installation

### Step 1: Download Files
Download these two files from the repository:
- `BrickLayersCuraScript.py`
- `bricklayers.py`

### Step 2: Locate Cura Scripts Folder
1. Open Ultimaker Cura
2. Go to **Help** → **Show Configuration Folder**
3. Navigate to the `scripts` subfolder
   - If the `scripts` folder doesn't exist, create it

### Step 3: Install Files
1. Copy both downloaded files into the `scripts` folder
2. Ensure the files are named exactly:
   - `BrickLayersCuraScript.py`
   - `bricklayers.py`

### Step 4: Restart Cura
Close and reopen Ultimaker Cura completely.

### Step 5: Enable BrickLayers
1. In Cura, go to **Extensions** → **Post Processing** → **Modify G-Code**
2. Click **Add a script**
3. Select **BrickLayers** from the dropdown list
4. Configure your settings (see Configuration section below)

## Configuration

### Basic Settings
- **Enable BrickLayers**: Check this box to activate the script
- **Start at layer**: Layer number to begin processing (recommended: 3)
- **Extrusion multiplier**: Scaling factor for extrusion (recommended: 1.05)
- **Layers to ignore**: Leave empty unless you need to skip specific layers

### Recommended Cura Settings
For best results with BrickLayers:

**Print Settings:**
- Layer Height: 0.2mm or 0.3mm
- Wall Line Count: 2-4 walls
- Infill: Any pattern works

**Advanced:**
- Print Sequence: "All at Once"
- Z Hop When Retracted: Enabled

## Troubleshooting

### Script Not Appearing
If BrickLayers doesn't appear in the post-processing scripts list:

1. **Check file location**: Ensure both files are in the correct `scripts` folder
2. **Check file names**: Files must be named exactly as specified
3. **Restart Cura**: Close Cura completely and reopen
4. **Check permissions**: Ensure Cura can read the files

### Common File Locations

**Windows:**
```
%APPDATA%\cura\[VERSION]\scripts\
```
Example: `C:\Users\YourName\AppData\Roaming\cura\5.0\scripts\`

**macOS:**
```
~/Library/Application Support/cura/[VERSION]/scripts/
```

**Linux:**
```
~/.local/share/cura/[VERSION]/scripts/
```

### Processing Issues

**Slow processing:**
- Normal for large files - BrickLayers analyzes every G-code line
- Consider testing with smaller models first

**Print quality issues:**
- Reduce extrusion multiplier to 1.02-1.03
- Increase starting layer number
- Check printer capabilities for modified travel moves

## Verification

To verify the installation worked:

1. Load a simple model in Cura
2. Enable BrickLayers in post-processing
3. Slice the model
4. Check the G-code preview - you should see the script listed as active
5. Look for "BRICK:" comments in the generated G-code

## Getting Help

If you encounter issues:

1. Check Cura's console output for error messages
2. Try with a simple test model first
3. Verify your G-code contains `;LAYER:` markers
4. Report issues on the GitHub repository

## Advanced Installation (Plugin Method)

For developers who want to package this as a proper Cura plugin:

1. Create a `plugin.json` file with proper metadata
2. Create an `__init__.py` file for plugin initialization
3. Package as a `.curapackage` file
4. Install through Cura's plugin manager

This method requires more technical knowledge but provides better integration.

