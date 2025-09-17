#!/usr/bin/env python3
"""
BrickLayers VSCode Debug Package
===============================

Complete debugging environment for BrickLayers Cura integration.
This package allows you to test and debug the BrickLayers script
in VSCode or any Python environment.

Features:
- Step-by-step debugging
- Error isolation
- Performance testing
- Output validation
- Cura simulation

Usage in VSCode:
1. Open this folder in VSCode
2. Set breakpoints in this file
3. Run with F5 or Ctrl+F5
4. Use the integrated debugger to step through

Command line usage:
    python vscode_debug_package.py [options]
    
Options:
    --file <gcode_file>     Use specific G-code file
    --layers <num>          Limit number of layers (default: 10)
    --verbose               Enable verbose output
    --profile               Enable performance profiling
"""

import sys
import os
import time
import traceback
import json
import argparse
from typing import List, Dict, Any, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class BrickLayersDebugger:
    """Comprehensive debugging class for BrickLayers"""
    
    def __init__(self, verbose: bool = False, profile: bool = False):
        self.verbose = verbose
        self.profile = profile
        self.results = {}
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with levels"""
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅", 
                "ERROR": "❌",
                "WARNING": "⚠️",
                "DEBUG": "🔍"
            }.get(level, "📝")
            print(f"{prefix} {message}")
    
    def time_operation(self, operation_name: str):
        """Context manager for timing operations"""
        class Timer:
            def __init__(self, debugger, name):
                self.debugger = debugger
                self.name = name
                self.start_time = None
                
            def __enter__(self):
                self.start_time = time.time()
                self.debugger.log(f"Starting {self.name}...", "DEBUG")
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                self.debugger.results[f"{self.name}_duration"] = duration
                self.debugger.log(f"Completed {self.name} in {duration:.3f}s", "SUCCESS")
                
        return Timer(self, operation_name)
    
    def test_imports(self) -> bool:
        """Test all required imports"""
        self.log("Testing imports...", "DEBUG")
        
        try:
            with self.time_operation("bricklayers_import"):
                import bricklayers
                self.log("bricklayers module imported", "SUCCESS")
                
            with self.time_operation("processor_class_check"):
                processor_class = getattr(bricklayers, 'BrickLayersProcessor', None)
                if not processor_class:
                    raise ImportError("BrickLayersProcessor not found")
                self.log("BrickLayersProcessor class found", "SUCCESS")
                
            with self.time_operation("script_import"):
                from BrickLayersCuraScript import BrickLayersCuraScript
                self.log("BrickLayersCuraScript imported", "SUCCESS")
                
            return True
            
        except Exception as e:
            self.log(f"Import failed: {e}", "ERROR")
            self.errors.append(f"Import error: {e}")
            return False
    
    def load_test_data(self, filename: Optional[str] = None, max_layers: int = 10) -> Optional[List[List[str]]]:
        """Load and parse test G-code data"""
        self.log(f"Loading test data (max {max_layers} layers)...", "DEBUG")
        
        # Try different test files
        test_files = [
            filename,
            "bricktest.gcode",
            "sample_gcode/Sample_3DBenchy_5walls_classic.gcode",
            "test_output.gcode"
        ]
        
        for test_file in test_files:
            if test_file and os.path.exists(test_file):
                try:
                    with self.time_operation("file_loading"):
                        with open(test_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                    
                    self.log(f"Loaded {len(lines)} lines from {test_file}", "SUCCESS")
                    
                    with self.time_operation("layer_parsing"):
                        layers = self._parse_layers(lines, max_layers)
                    
                    self.log(f"Parsed into {len(layers)} layers", "SUCCESS")
                    self.results["input_file"] = test_file
                    self.results["input_lines"] = len(lines)
                    self.results["input_layers"] = len(layers)
                    
                    return layers
                    
                except Exception as e:
                    self.log(f"Failed to load {test_file}: {e}", "WARNING")
                    continue
        
        # Create minimal test data if no file found
        self.log("Creating minimal test data", "WARNING")
        return self._create_minimal_data()
    
    def _parse_layers(self, lines: List[str], max_layers: int) -> List[List[str]]:
        """Parse G-code lines into layer structure"""
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
                if layer_count > max_layers:
                    break
            else:
                current_layer.append(line)
        
        if current_layer:
            layers.append(current_layer)
            
        return layers
    
    def _create_minimal_data(self) -> List[List[str]]:
        """Create minimal test data"""
        return [
            [";LAYER:0", "G1 X10 Y10 E1", "G1 X20 Y10 E2"],
            [";LAYER:1", "G1 X10 Y20 E3", "G1 X20 Y20 E4"],
            [";LAYER:2", "G1 X10 Y30 E5", "G1 X20 Y30 E6"]
        ]
    
    def test_script_creation(self) -> Optional[Any]:
        """Test script creation and configuration"""
        self.log("Testing script creation...", "DEBUG")
        
        try:
            with self.time_operation("script_creation"):
                from BrickLayersCuraScript import BrickLayersCuraScript
                script = BrickLayersCuraScript()
            
            with self.time_operation("settings_test"):
                settings_json = script.getSettingDataString()
                settings_data = json.loads(settings_json)
                self.log(f"Settings JSON valid: {len(settings_data)} keys", "SUCCESS")
            
            # Configure script
            script.settings = {
                "enabled": True,
                "start_at_layer": 2,
                "extrusion_multiplier": 1.05,
                "layers_to_ignore": ""
            }
            
            self.results["script_created"] = True
            self.results["settings_keys"] = len(settings_data)
            
            return script
            
        except Exception as e:
            self.log(f"Script creation failed: {e}", "ERROR")
            self.errors.append(f"Script creation error: {e}")
            return None
    
    def test_processing(self, script: Any, test_data: List[List[str]]) -> Optional[List[List[str]]]:
        """Test G-code processing"""
        self.log("Testing G-code processing...", "DEBUG")
        
        try:
            # Validate input data
            with self.time_operation("input_validation"):
                self._validate_input_data(test_data)
            
            # Process the data
            with self.time_operation("gcode_processing"):
                result = script.execute(test_data)
            
            # Validate output data
            with self.time_operation("output_validation"):
                self._validate_output_data(result)
            
            self.results["processing_successful"] = True
            self.results["output_layers"] = len(result)
            self.results["output_lines"] = sum(len(layer) for layer in result)
            
            return result
            
        except Exception as e:
            self.log(f"Processing failed: {e}", "ERROR")
            self.errors.append(f"Processing error: {e}")
            traceback.print_exc()
            return None
    
    def _validate_input_data(self, data: List[List[str]]):
        """Validate input data structure"""
        if not isinstance(data, list):
            raise TypeError(f"Expected list, got {type(data)}")
        
        for i, layer in enumerate(data):
            if not isinstance(layer, list):
                raise TypeError(f"Layer {i} is not a list: {type(layer)}")
            
            for j, line in enumerate(layer):
                if not isinstance(line, str):
                    raise TypeError(f"Layer {i}, line {j} is not a string: {type(line)}")
        
        self.log(f"Input validation passed: {len(data)} layers", "SUCCESS")
    
    def _validate_output_data(self, data: List[List[str]]):
        """Validate output data structure"""
        if not isinstance(data, list):
            raise TypeError(f"Expected list, got {type(data)}")
        
        for i, layer in enumerate(data):
            if not isinstance(layer, list):
                raise TypeError(f"Output layer {i} is not a list: {type(layer)}")
            
            for j, line in enumerate(layer):
                if not isinstance(line, str):
                    raise TypeError(f"Output layer {i}, line {j} is not a string: {type(line)} - Content: {repr(line)}")
        
        self.log(f"Output validation passed: {len(data)} layers", "SUCCESS")
    
    def test_file_writing(self, data: List[List[str]], filename: str = "debug_output.gcode") -> bool:
        """Test file writing process"""
        self.log(f"Testing file writing to {filename}...", "DEBUG")
        
        try:
            with self.time_operation("file_writing"):
                with open(filename, 'w', encoding='utf-8') as f:
                    for layer in data:
                        for line in layer:
                            if not isinstance(line, str):
                                raise TypeError(f"Cannot write non-string: {type(line)} - {repr(line)}")
                            f.write(line + "\n")
            
            # Verify file
            with open(filename, 'r', encoding='utf-8') as f:
                written_lines = f.readlines()
            
            self.results["file_written"] = True
            self.results["file_lines"] = len(written_lines)
            self.log(f"File written successfully: {len(written_lines)} lines", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"File writing failed: {e}", "ERROR")
            self.errors.append(f"File writing error: {e}")
            return False
    
    def run_full_test(self, filename: Optional[str] = None, max_layers: int = 10) -> Dict[str, Any]:
        """Run complete test suite"""
        self.log("Starting BrickLayers debugging session", "INFO")
        
        # Test imports
        if not self.test_imports():
            return self._generate_report()
        
        # Load test data
        test_data = self.load_test_data(filename, max_layers)
        if not test_data:
            return self._generate_report()
        
        # Test script creation
        script = self.test_script_creation()
        if not script:
            return self._generate_report()
        
        # Test processing
        result = self.test_processing(script, test_data)
        if not result:
            return self._generate_report()
        
        # Test file writing
        self.test_file_writing(result)
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "results": self.results,
            "summary": self._generate_summary()
        }
        
        self.log("=" * 50, "INFO")
        if report["success"]:
            self.log("🎉 ALL TESTS PASSED!", "SUCCESS")
        else:
            self.log(f"❌ {len(self.errors)} ERRORS FOUND", "ERROR")
        
        self.log("Test Summary:", "INFO")
        for key, value in report["summary"].items():
            self.log(f"  {key}: {value}", "INFO")
        
        if self.errors:
            self.log("Errors:", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        return {
            "Total errors": len(self.errors),
            "Input file": self.results.get("input_file", "None"),
            "Input layers": self.results.get("input_layers", 0),
            "Output layers": self.results.get("output_layers", 0),
            "Processing time": f"{self.results.get('gcode_processing_duration', 0):.3f}s",
            "File written": self.results.get("file_written", False)
        }

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="BrickLayers VSCode Debug Package")
    parser.add_argument("--file", help="G-code file to test with")
    parser.add_argument("--layers", type=int, default=10, help="Maximum layers to process")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--profile", action="store_true", help="Enable performance profiling")
    
    args = parser.parse_args()
    
    # Create debugger
    debugger = BrickLayersDebugger(verbose=args.verbose, profile=args.profile)
    
    # Run tests
    report = debugger.run_full_test(args.file, args.layers)
    
    # Exit with appropriate code
    sys.exit(0 if report["success"] else 1)

if __name__ == "__main__":
    main()

