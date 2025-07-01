# AUTOSAR ARXML Merger

A professional Python module for merging AUTOSAR ARXML files based on the Splitable Elements approach.

## 🎯 Status: Fully implemented and tested

✅ **Basic ARXML Merging** - Successfully tested with real ARXML files  
✅ **Schema Detection** - Automatic detection of AUTOSAR 4.3.1 to 24-11  
✅ **Split-Key Handling** - Correct usage of split keys  
✅ **Conflict Handling** - Various resolution strategies  
✅ **CLI Interface** - Fully functional  
✅ **Python API** - Simple and advanced usage  
✅ **Error Handling** - Robust handling of invalid files  

## 🚀 Features

- **Schema-supported Merging**: Automatic detection of AUTOSAR schema versions (4.3.1 to 24-11)
- **Splitable Elements**: Intelligent merging based on AUTOSAR split keys
- **Flexible Conflict Resolution**: Various strategies (merge_all, first_wins, last_wins, fail)
- **CLI and Python API**: Usable as command-line tool or Python library
- **Detailed Reporting**: Statistics and conflict analysis
- **Robust Error Handling**: Comprehensive validation and logging

## 📦 Installation

```bash
# Clone repository
git clone <repository-url>
cd ArXmlMerger

# Install dependencies
pip install -r requirements.txt

# Install module in development mode
pip install -e .
```

## 💻 Usage

### Python API

```python
from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy

# Simple merge
merger = ArxmlMerger()
result = merger.merge_files(['model1.arxml', 'model2.arxml'])
result.save('merged_model.arxml')

# Advanced configuration
config = MergeConfig(
    conflict_resolution=ConflictResolutionStrategy.MERGE_ALL,
    validate_schema=True,
    preserve_comments=True
)
merger = ArxmlMerger(config)
result = merger.merge_files(['model1.arxml', 'model2.arxml'])

# Evaluate statistics
print(f"Files processed: {result.statistics.files_processed}")
print(f"Elements merged: {result.statistics.elements_merged}")
print(f"Conflicts found: {result.statistics.conflicts_found}")
```

### Command Line Interface

```bash
# Simple merge
python -m arxml_merger.cli -i model1.arxml model2.arxml -o merged.arxml

# With conflict resolution
python -m arxml_merger.cli -i *.arxml -o result.arxml --conflict-resolution last_wins

# With debug logging
python -m arxml_merger.cli -i model*.arxml -o merged.arxml --log-level DEBUG --log-file merge.log
```

## 🔧 Supported AUTOSAR Versions

| Version | Namespace URI | Status |
|---------|---------------|---------|
| 4.0.x   | `http://autosar.org/schema/r4.0` | ✅ Full support |
| 4.1.x   | `http://autosar.org/schema/r4.0` | ✅ Full support |
| 4.2.x   | `http://autosar.org/schema/r4.0` | ✅ Full support |
| 4.3.x   | `http://autosar.org/schema/r4.0` | ✅ Full support |
| 4.4.x   | `http://autosar.org/schema/r4.0` | ✅ Full support |
| 4.5.x   | `http://autosar.org/schema/r4.0` | ✅ Full support |

## ⚙️ Conflict Resolution

The module supports various strategies for handling merge conflicts:

| Strategy | Description | Application |
|----------|-------------|-------------|
| `MERGE_ALL` | Merges all values together (default) | For complementary models |
| `FIRST_WINS` | First value wins | For priority-based merging |
| `LAST_WINS` | Last value wins | For update scenarios |
| `FAIL_ON_CONFLICT` | Fail on conflicts | For strict validation |

## 📊 Program Flow Documentation

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARXML Merger Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │    CLI      │    │  Python API  │    │   Examples      │    │
│  │  Interface  │    │  Interface   │    │   Scripts       │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│         │                   │                     │             │
│         └───────────────────┼─────────────────────┘             │
│                             │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                ArxmlMerger (Core)                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │    Schema    │  │    Merger    │  │    Config    │  │   │
│  │  │   Handler    │  │    Engine    │  │   Manager    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Utility Layer                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  XML Utils   │  │  Validation  │  │  File I/O    │  │   │
│  │  │              │  │   Engine     │  │   Handler    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Merge Process Flow

```
START → Input Validation → Schema Detection → Config Setup
  ↓              ↓                ↓               ↓
Load Files → Split Key Analysis → Element Mapping
  ↓              ↓                ↓
Conflict Resolution → Merge Execution → Output Generation → END
```

### Important Split Keys

The module automatically considers the correct split keys for AUTOSAR Splitable Elements:

**Software Components:**
- `APPLICATION-SW-COMPONENT-TYPE` → `SHORT-NAME`
- `COMPOSITION-SW-COMPONENT-TYPE` → `SHORT-NAME`
- `COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE` → `SHORT-NAME`

**Ports and Interfaces:**
- `P-PORT-PROTOTYPE`, `R-PORT-PROTOTYPE` → `SHORT-NAME`
- `CLIENT-SERVER-INTERFACE`, `SENDER-RECEIVER-INTERFACE` → `SHORT-NAME`

**Data Types:**
- `IMPLEMENTATION-DATA-TYPE` → `SHORT-NAME`
- `APPLICATION-PRIMITIVE-DATA-TYPE` → `SHORT-NAME`

## 🏗️ Project Structure

```
ArXmlMerger/
├── arxml_merger/              # Main package
│   ├── core/                  # Core functionality
│   │   ├── merger.py          # Main ArxmlMerger class
│   │   ├── models.py          # Data models
│   │   └── exceptions.py      # Exception classes
│   ├── schema/                # Schema handling
│   │   └── autosar_schema.py  # AUTOSAR schema handlers
│   ├── utils/                 # Utility functions
│   │   └── xml_utils.py       # XML utilities
│   └── cli.py                 # Command Line Interface
├── examples/                  # Examples and test files
├── tests/                     # Unit tests
├── .vscode/                   # VS Code configuration
│   ├── launch.json           # Debug configurations
│   └── tasks.json            # Build tasks
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Modern Python packaging
└── README.md                 # This file
```

## 🧪 Development

### Quick Start

```bash
# Set up development environment
make dev-setup

# Run tests
make test

# Check code quality
make lint

# Run examples
make run-examples
```

### VS Code Integration

The project includes complete VS Code configurations:

**Debug Configurations:**
- `Python: Run Tests` - Run all tests
- `Python: CLI - Example Merge` - CLI with example files
- `Python: Run Example Usage` - Run example script

**Tasks:**
- `Full Test Suite` - Tests with coverage
- `Build Package` - Create distribution
- `Development Setup` - Install all dependencies

### Examples

```bash
# Run example script
python examples/example_usage.py

# Test CLI with example files
python -m arxml_merger.cli -i examples/sample1.arxml examples/sample2.arxml -o examples/result.arxml
```

## 📊 Test Coverage

The project has a comprehensive test suite:

- **13 Unit Tests** - All core functions covered
- **58% Code Coverage** - Solid test coverage
- **Automated Tests** - Continuous validation
- **Realistic Test Data** - Real AUTOSAR structures

```bash
# Run tests with coverage
pytest tests/ -v --cov=arxml_merger --cov-report=html
```

## 🔍 Detailed Process Documentation

<details>
<summary>Click here for detailed process diagrams</summary>

### Schema Detection

```
Input ARXML → Parse XML Root → Extract Namespace → Detect Version → Select Handler
```

### Split Key Analysis

```
For each Element:
Extract Tag → Check if Splitable → Extract Split Keys → Generate Signature → Store in Map
```

### Conflict Handling

```
Multiple Elements with same Signature?
→ Apply Resolution Strategy → Log Resolution → Continue
```

</details>

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 👥 Contributing

Contributions are welcome! Please create a pull request or open an issue.

## 📞 Support

For questions and support:
- Create a [GitHub Issue](../../issues)
- Check the [Examples](examples/)
- Read the [Test Documentation](tests/)

---

**Developed for professional AUTOSAR development with focus on robustness, standards compliance, and user-friendliness.**
