# Changelog

All notable changes to the BrickLayers Cura integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-cura] - 2025-09-17

### Added
- Initial Cura integration of the BrickLayers algorithm
- Native Cura post-processing script interface
- Automatic G-code processing within Cura workflow
- Comprehensive documentation and installation guide
- Test suite for validation and debugging
- GitHub workflows for automated testing
- Sample files and examples adapted for Cura

### Changed
- Adapted original BrickLayers algorithm for Cura's G-code format
- Modified layer detection to work with Cura's `;LAYER:` markers
- Updated documentation format to match original repository structure

### Fixed
- Null pointer errors in `bricklayers.py` for Cura compatibility
- G-code feature detection for Cura's wall type naming
- Layer boundary reconstruction for Cura's output format

### Technical Details
- Based on GeekDetour/BrickLayers v0.2.1
- Compatible with Cura 4.x and 5.x
- Supports standard Cura G-code format
- Tested with multiple G-code samples

### Files Added
- `BrickLayersCuraScript.py` - Main Cura integration script
- `bricklayers.py` - Core algorithm with Cura compatibility fixes
- `README.md` - Comprehensive documentation
- `INSTALLATION.md` - Detailed installation guide
- `CHANGELOG.md` - Version history
- `sample_tests/cura_test.py` - Cura-specific test script
- `.github/workflows/` - Automated testing workflows
- `docs/` - Documentation images and assets
- `sample_*` - Sample files for testing and demonstration

### Installation
1. Download `BrickLayersCuraScript.py` and `bricklayers.py`
2. Place in Cura's `scripts` folder (Help → Show Configuration Folder → scripts)
3. Restart Cura
4. Enable via Extensions → Post Processing → Modify G-Code

### Credits
- Original algorithm: [GeekDetour/BrickLayers](https://github.com/GeekDetour/BrickLayers)
- Cura integration: Adapted for Ultimaker Cura compatibility
- Testing and validation: Comprehensive test suite created

