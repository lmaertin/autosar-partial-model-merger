# ARXML Merger Examples

This directory contains organized examples demonstrating the AUTOSAR ARXML merger functionality.

## Directory Structure

```
examples/
├── README.md                    # This file
├── basic_merge/                 # Basic merge examples
│   ├── engine_control_base.arxml      # Base engine control model
│   └── engine_control_extended.arxml  # Extended engine control model  
├── conflict_scenarios/          # Examples showing conflict resolution
│   ├── sensor_model_v1.arxml          # Sensor model version 1
│   └── sensor_model_v2.arxml          # Sensor model version 2
├── scripts/                     # Python demonstration scripts
│   ├── basic_merge_demo.py            # Library usage examples
│   └── cli_demo.py                    # CLI usage examples
└── generated/                   # Output directory for generated files
    └── (generated files are placed here)
```

## Example Files Description

### Basic Merge Examples (`basic_merge/`)

**engine_control_base.arxml**
- Basic AUTOSAR engine control component
- Contains: ComponentTypes, Interfaces, DataTypes packages
- Schema: AUTOSAR 19-11
- Use case: Foundation model for engine management

**engine_control_extended.arxml**  
- Extended version of the engine control component
- Contains: Additional ports, behaviors, events, and system mappings
- Schema: AUTOSAR 19-11
- Use case: Enhanced model with additional functionality

### Conflict Scenarios (`conflict_scenarios/`)

**sensor_model_v1.arxml**
- Basic sensor component model
- Contains: Temperature sensor with Float32 data type
- Schema: AUTOSAR 19-11
- Use case: Version 1 of a sensor model

**sensor_model_v2.arxml**
- Enhanced sensor component model  
- Contains: Temperature + Pressure sensors with additional data elements
- Schema: AUTOSAR 19-11
- Use case: Version 2 with conflicts for testing resolution strategies

## Usage Examples

### 1. Using the Python Library

```python
# Run the basic demo script
python examples/scripts/basic_merge_demo.py

# This demonstrates:
# - Different merge strategies (merge_all, first_wins, last_wins)
# - Conflict resolution scenarios
# - Library API usage patterns
```

### 2. Using the CLI

```bash
# Basic merge
python -m arxml_merger.cli \
  -i examples/basic_merge/engine_control_base.arxml \
     examples/basic_merge/engine_control_extended.arxml \
  -o examples/generated/merged_basic.arxml

# Verbose merge with conflict resolution
python -m arxml_merger.cli \
  -i examples/conflict_scenarios/sensor_model_v1.arxml \
     examples/conflict_scenarios/sensor_model_v2.arxml \
  -o examples/generated/merged_conflicts.arxml \
  --conflict-resolution first_wins \
  --verbose-merge

# Run CLI demo script for comprehensive examples
python examples/scripts/cli_demo.py
```

### 3. Using VS Code Launch Configurations

The project includes pre-configured launch configurations in `.vscode/launch.json`:

- **"Python: CLI - Basic Merge"** - Basic merge operation
- **"Python: CLI - Verbose Debug"** - Verbose merge with debug output
- **"Python: CLI - First Wins Strategy"** - Demonstrates first wins conflict resolution
- **"Python: CLI - Last Wins Strategy"** - Demonstrates last wins conflict resolution
- **"Python: Run Example Script"** - Runs the basic demo script

## Merge Strategies Explained

### merge_all (Default)
- Combines all elements from input files
- Creates comprehensive merged model
- Preserves maximum information

### first_wins
- In case of conflicts, keeps elements from the first input file
- Useful when prioritizing a base model
- Predictable conflict resolution

### last_wins  
- In case of conflicts, keeps elements from the last input file
- Useful when applying updates/patches
- Latest changes take precedence

## Expected Conflicts

When merging the example files, you may encounter these typical conflicts:

1. **UUID conflicts** - Same element types with different UUIDs
2. **Interface extensions** - Additional data elements in interfaces
3. **Port additions** - New ports added to components
4. **Behavioral differences** - Different internal behaviors

These conflicts are intentional and demonstrate the merger's conflict detection and resolution capabilities.

## Schema Information

All example files use **AUTOSAR Schema 19-11** (R19-11):
- Namespace: `http://autosar.org/schema/r4.0`
- Schema Location: `AUTOSAR_19-11.xsd`
- Encoding: UTF-8

## Generated Files

The `generated/` directory is used for:
- Output files from example scripts
- CLI command results  
- Test merge results
- Temporary files during development

**Note**: Generated files are excluded from git tracking via `.gitignore`.

## Getting Started

1. Ensure the ARXML merger is installed and working
2. Run the basic demo: `python examples/scripts/basic_merge_demo.py`
3. Try CLI examples: `python examples/scripts/cli_demo.py`
4. Explore VS Code launch configurations for interactive debugging
5. Experiment with your own ARXML files using these examples as templates
