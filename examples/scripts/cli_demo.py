#!/usr/bin/env python3
"""
CLI Demo Scripts
This script demonstrates various CLI usage patterns for the ARXML merger.
"""

import subprocess
import sys
from pathlib import Path

def run_cli_command(command, description):
    """Run a CLI command and display the result."""
    print(f"\n{'='*60}")
    print(f"Demo: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("❌ ERROR")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
                
    except Exception as e:
        print(f"❌ Failed to run command: {e}")

def main():
    """Demonstrate various CLI usage patterns."""
    print("ARXML Merger CLI Demo")
    print("====================")
    
    # Check if we're in the right directory
    project_root = Path(__file__).parent.parent.parent
    if not (project_root / "arxml_merger").exists():
        print("❌ Please run this script from the project root directory")
        return
    
    # Demo 1: Basic merge
    run_cli_command([
        sys.executable, "-m", "arxml_merger.cli",
        "-i", "examples/basic_merge/engine_control_base.arxml", 
              "examples/basic_merge/engine_control_extended.arxml",
        "-o", "examples/generated/cli_demo_basic.arxml"
    ], "Basic merge with default settings")
    
    # Demo 2: Verbose merge with first wins strategy
    run_cli_command([
        sys.executable, "-m", "arxml_merger.cli",
        "-i", "examples/basic_merge/engine_control_base.arxml", 
              "examples/basic_merge/engine_control_extended.arxml",
        "-o", "examples/generated/cli_demo_first_wins.arxml",
        "--conflict-resolution", "first_wins",
        "--verbose-merge"
    ], "First wins strategy with verbose output")
    
    # Demo 3: Last wins strategy with debug logging
    run_cli_command([
        sys.executable, "-m", "arxml_merger.cli",
        "-i", "examples/basic_merge/engine_control_base.arxml", 
              "examples/basic_merge/engine_control_extended.arxml",
        "-o", "examples/generated/cli_demo_last_wins.arxml",
        "--conflict-resolution", "last_wins",
        "--log-level", "DEBUG"
    ], "Last wins strategy with debug logging")
    
    # Demo 4: Conflict scenarios
    run_cli_command([
        sys.executable, "-m", "arxml_merger.cli",
        "-i", "examples/conflict_scenarios/sensor_model_v1.arxml",
              "examples/conflict_scenarios/sensor_model_v2.arxml",
        "-o", "examples/generated/cli_demo_conflicts.arxml",
        "--conflict-resolution", "merge_all",
        "--verbose-merge",
        "--log-level", "INFO"
    ], "Conflict resolution demo with sensor models")
    
    # Demo 5: Help command
    run_cli_command([
        sys.executable, "-m", "arxml_merger.cli",
        "--help"
    ], "Display CLI help")
    
    print(f"\n🎉 CLI Demo completed!")
    print(f"Generated files are in: examples/generated/")

if __name__ == "__main__":
    main()
