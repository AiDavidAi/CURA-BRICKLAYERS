# BrickLayers for Ultimaker Cura

A post-processing script that implements the BrickLayers algorithm for Ultimaker Cura, creating interlocking layers that significantly improve the strength of 3D printed parts.

## What is BrickLayers?

BrickLayers transforms the arrangement of perimeter beads in your G-code from a rectangular pattern to a hexagonal pattern, similar to how bricks are laid in construction. This creates stronger interlocking between layers, dramatically improving part strength.

**Key Benefits:**
- 🔧 **Stronger Parts**: Significantly improved layer adhesion and part strength
- 🎯 **Easy Integration**: Works as a post-processing script in Cura
- ⚙️ **Configurable**: Adjustable settings for different print requirements
- 🔄 **Compatible**: Works with existing Cura workflows and settings

## Video Demonstration

For a detailed explanation of the BrickLayers technique, watch:
- [Brick Layers: Stronger 3D Prints TODAY - instead of 2040](https://youtu.be/9IdNA_hWiyE)

## Installation

### Method 1: Manual Installation (Recommended)

1. **Download the files**: Download `BrickLayersCuraScript.py` and `bricklayers.py` from this repository
2. **Find Cura's scripts folder**: 
   - Open Ultimaker Cura
   - Go to **Help → Show Configuration Folder**
   - Navigate to the `scripts` subfolder
3. **Copy the files**: Place both files in the `scripts` folder
4. **Restart Cura**: Close and reopen Ultimaker Cura

### Method 2: Plugin Installation (Advanced)

For advanced users, you can package this as a proper Cura plugin by creating a `plugin.json` file and following Cura's plugin development guidelines.

## Usage

1. **Enable the script**:
   - In Cura, go to **Extensions → Post Processing → Modify G-Code**
   - Click **Add a script**
   - Select **BrickLayers** from the list

2. **Configure settings**:
   - **Enable BrickLayers**: Check to activate the script
   - **Start at layer**: Layer number to begin BrickLayers processing (default: 3)
   - **Extrusion multiplier**: Scaling factor for extrusion (default: 1.05)
   - **Layers to ignore**: Comma-separated list of layers to skip

3. **Slice and print**: Slice your model normally - BrickLayers will process the G-code automatically

## Settings Explained

### Start at Layer
- **Default**: 3
- **Purpose**: Skips the first few layers to ensure good bed adhesion
- **Recommendation**: Keep at 3 unless you have specific requirements

### Extrusion Multiplier
- **Default**: 1.05 (5% increase)
- **Purpose**: Compensates for the redistribution of material
- **Range**: 0.5 to 2.0
- **Tuning**: Start with 1.05 and adjust based on print quality

### Layers to Ignore
- **Default**: Empty
- **Purpose**: Skip BrickLayers processing on specific layers
- **Format**: Comma-separated numbers (e.g., "5,10,15")
- **Use case**: Skip layers with complex geometry or overhangs

## Cura Settings Recommendations

For best results with BrickLayers:

### Print Settings
- **Layer Height**: 0.2mm or 0.3mm work well
- **Wall Line Count**: 2-4 walls recommended
- **Infill**: Any infill pattern works

### Advanced Settings
- **Print Sequence**: "All at Once" (avoid "One at a Time")
- **Z Hop**: Enable for better travel moves

## Troubleshooting

### Common Issues

**Script not appearing in the list:**
- Ensure both files are in the correct `scripts` folder
- Restart Cura completely
- Check that file names are exactly: `BrickLayersCuraScript.py` and `bricklayers.py`

**Print quality issues:**
- Try reducing the extrusion multiplier to 1.02-1.03
- Increase the starting layer if first layers are problematic
- Check that your printer can handle the modified travel moves

**Processing takes too long:**
- This is normal for large files - BrickLayers processes every line of G-code
- Consider using fewer layers for testing

### Getting Help

If you encounter issues:
1. Check the Cura console for error messages
2. Try with a simple test model first
3. Verify your G-code contains the expected layer markers (`;LAYER:`)

## Technical Details

### How It Works
1. **G-code Analysis**: Parses the sliced G-code to identify wall segments
2. **Layer Redistribution**: Moves inner perimeter segments to create interlocking patterns
3. **Path Optimization**: Adjusts travel moves and retractions for the new layout
4. **Output Generation**: Produces modified G-code with BrickLayers enhancements

### Compatibility
- **Cura Version**: Tested with Cura 4.x and 5.x
- **G-code Format**: Standard Cura G-code with `;LAYER:` markers
- **Printers**: Compatible with any printer that works with Cura

## Credits

- **Original BrickLayers Algorithm**: [GeekDetour/BrickLayers](https://github.com/GeekDetour/BrickLayers)
- **Cura Integration**: Adapted for Ultimaker Cura compatibility
- **Patent**: The hexagonal 3D printing pattern is public domain (Batchelder: US005653925A, 1995)

## License

This project follows the same license as the original BrickLayers project. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Support

If you find this useful, consider supporting the original BrickLayers development:
- [GeekDetour on Patreon](https://www.patreon.com/c/GeekDetour)

