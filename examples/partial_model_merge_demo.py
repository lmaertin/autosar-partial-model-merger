"""
Comprehensive example demonstrating AUTOSAR Partial Model Merge standard compliance
"""

from pathlib import Path
import tempfile
from lxml import etree

from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy


def create_comprehensive_example():
    """Creates a comprehensive example showing AUTOSAR Partial Model Merge functionality"""
    
    # Base model with UUID identifiers
    base_model = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE UUID="pkg-base-001">
            <SHORT-NAME>BaseSystem</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE UUID="comp-engine-001">
                    <SHORT-NAME>EngineControl</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE UUID="port-throttle-001">
                            <SHORT-NAME>ThrottlePosition</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                        <R-PORT-PROTOTYPE UUID="port-speed-001">
                            <SHORT-NAME>VehicleSpeed</SHORT-NAME>
                        </R-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
                <CLIENT-SERVER-INTERFACE UUID="iface-diag-001">
                    <SHORT-NAME>DiagnosticInterface</SHORT-NAME>
                </CLIENT-SERVER-INTERFACE>
            </ELEMENTS>
        </AR-PACKAGE>
        <AR-PACKAGE UUID="pkg-types-001">
            <SHORT-NAME>DataTypes</SHORT-NAME>
            <ELEMENTS>
                <IMPLEMENTATION-DATA-TYPE UUID="type-uint32-001">
                    <SHORT-NAME>UInt32Type</SHORT-NAME>
                </IMPLEMENTATION-DATA-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""

    # Extension model adding new elements to existing components
    extension_model = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE UUID="pkg-base-001">
            <SHORT-NAME>BaseSystem</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE UUID="comp-engine-001">
                    <SHORT-NAME>EngineControl</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE UUID="port-rpm-002">
                            <SHORT-NAME>EngineRPM</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                        <R-PORT-PROTOTYPE UUID="port-temp-002">
                            <SHORT-NAME>CoolantTemperature</SHORT-NAME>
                        </R-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
                <SENDER-RECEIVER-INTERFACE UUID="iface-sensors-002">
                    <SHORT-NAME>SensorInterface</SHORT-NAME>
                </SENDER-RECEIVER-INTERFACE>
            </ELEMENTS>
        </AR-PACKAGE>
        <AR-PACKAGE UUID="pkg-adaptive-002">
            <SHORT-NAME>AdaptiveApplications</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE UUID="comp-adaptive-002">
                    <SHORT-NAME>AdaptiveService</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE UUID="port-service-002">
                            <SHORT-NAME>ServicePort</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""

    # Third model with conflicting element (same UUID, different content)
    conflict_model = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE UUID="pkg-types-001">
            <SHORT-NAME>DataTypes</SHORT-NAME>
            <ELEMENTS>
                <IMPLEMENTATION-DATA-TYPE UUID="type-uint32-001">
                    <SHORT-NAME>UInt32Type</SHORT-NAME>
                    <!-- This represents updated content for the same UUID -->
                </IMPLEMENTATION-DATA-TYPE>
                <IMPLEMENTATION-DATA-TYPE UUID="type-float64-003">
                    <SHORT-NAME>Float64Type</SHORT-NAME>
                </IMPLEMENTATION-DATA-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""

    return base_model, extension_model, conflict_model


def demonstrate_partial_model_merge():
    """Demonstrates the AUTOSAR Partial Model Merge functionality"""
    
    print("AUTOSAR Partial Model Merge - Standard Compliance Demo")
    print("=" * 60)
    
    # Create test models
    base_model, extension_model, conflict_model = create_comprehensive_example()
    
    # Create temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        base_file = temp_path / "base_model.arxml"
        extension_file = temp_path / "extension_model.arxml"
        conflict_file = temp_path / "conflict_model.arxml"
        
        base_file.write_text(base_model, encoding='utf-8')
        extension_file.write_text(extension_model, encoding='utf-8')
        conflict_file.write_text(conflict_model, encoding='utf-8')
        
        # Test different merge scenarios
        scenarios = [
            {
                "name": "Basic Partial Model Merge",
                "files": [base_file, extension_file],
                "strategy": ConflictResolutionStrategy.MERGE_ALL,
                "description": "Merging base model with extension using UUID-based identification"
            },
            {
                "name": "Three-Way Merge with Conflicts",
                "files": [base_file, extension_file, conflict_file],
                "strategy": ConflictResolutionStrategy.LAST_WINS,
                "description": "Merging three models with UUID conflicts resolved by last-wins strategy"
            },
            {
                "name": "Conservative Merge",
                "files": [base_file, extension_file],
                "strategy": ConflictResolutionStrategy.FIRST_WINS,
                "description": "Conservative merge prioritizing base model content"
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['name']}")
            print("-" * len(scenario['name']))
            print(f"Description: {scenario['description']}")
            print(f"Input files: {len(scenario['files'])}")
            print(f"Strategy: {scenario['strategy'].value}")
            
            try:
                # Configure merger for partial model merge
                config = MergeConfig(
                    conflict_resolution=scenario['strategy'],
                    preserve_comments=True,
                    verbose_merge=True
                )
                
                merger = ArxmlMerger(config)
                result = merger.merge_files(scenario['files'])
                
                # Analyze results
                print(f"✅ Merge successful!")
                print(f"   Files processed: {result.statistics.files_processed}")
                print(f"   Elements merged: {result.statistics.elements_merged}")
                print(f"   Conflicts found: {result.statistics.conflicts_found}")
                print(f"   Processing time: {result.statistics.processing_time:.3f}s")
                
                # Analyze merged content
                analyze_merged_content(result.merged_tree)
                
                # Save result
                output_file = temp_path / f"merged_{scenario['name'].lower().replace(' ', '_')}.arxml"
                result.save(output_file)
                print(f"   Saved to: {output_file.name}")
                
            except Exception as e:
                print(f"❌ Merge failed: {e}")


def analyze_merged_content(merged_tree):
    """Analyzes the merged content to demonstrate AUTOSAR compliance"""
    
    # Count different element types
    packages = []
    components = []
    ports = []
    interfaces = []
    data_types = []
    
    for element in merged_tree.iter():
        tag = etree.QName(element).localname
        
        if tag == "AR-PACKAGE":
            packages.append(element)
        elif tag.endswith("-SW-COMPONENT-TYPE"):
            components.append(element)
        elif tag.endswith("-PORT-PROTOTYPE"):
            ports.append(element)
        elif tag.endswith("-INTERFACE"):
            interfaces.append(element)
        elif tag.endswith("-DATA-TYPE"):
            data_types.append(element)
    
    print(f"   Content analysis:")
    print(f"     AR-PACKAGES: {len(packages)}")
    print(f"     Components: {len(components)}")
    print(f"     Ports: {len(ports)}")
    print(f"     Interfaces: {len(interfaces)}")
    print(f"     Data Types: {len(data_types)}")
    
    # Demonstrate UUID-based identification
    uuid_elements = []
    for element in merged_tree.iter():
        if element.get("UUID"):
            uuid_elements.append(element)
    
    print(f"     Elements with UUID: {len(uuid_elements)}")
    
    # Show some sample UUIDs
    if uuid_elements:
        print(f"     Sample UUIDs:")
        for element in uuid_elements[:3]:
            tag = etree.QName(element).localname
            uuid = element.get("UUID")
            short_name = ""
            for child in element:
                if etree.QName(child).localname == "SHORT-NAME" and child.text:
                    short_name = child.text
                    break
            print(f"       {tag}[{short_name}]: {uuid}")


def test_standard_compliance():
    """Tests specific AUTOSAR Partial Model Merge standard requirements"""
    
    print("\nAUTOSAR Standard Compliance Tests")
    print("=" * 40)
    
    from arxml_merger.schema.autosar_schema import SchemaDetector
    
    # Test schema detection and handler creation
    print("✅ Schema Detection:")
    for version in ["4.0", "4.3.1", "4.4", "20-11", "24-11"]:
        handler = SchemaDetector.create_schema_handler(version)
        print(f"   {version}: {handler.__class__.__name__}")
    
    # Test splitable elements classification
    print("\n✅ Splitable Elements Classification:")
    handler = SchemaDetector.create_schema_handler("4.0")
    
    splitable_samples = [
        "AR-PACKAGE", "APPLICATION-SW-COMPONENT-TYPE", "P-PORT-PROTOTYPE",
        "CLIENT-SERVER-INTERFACE", "IMPLEMENTATION-DATA-TYPE"
    ]
    
    non_splitable_samples = [
        "PORTS", "ELEMENTS", "SHORT-NAME", "INTERNAL-BEHAVIORS"
    ]
    
    for element in splitable_samples:
        is_splitable = handler.is_splitable_element(element)
        split_keys = handler.get_element_split_keys(element)
        print(f"   {element}: {'✓' if is_splitable else '✗'} (keys: {split_keys})")
    
    print(f"\n   Non-splitable elements correctly identified:")
    for element in non_splitable_samples:
        is_splitable = handler.is_splitable_element(element)
        print(f"   {element}: {'✗' if not is_splitable else '✓ (ERROR)'}")
    
    # Test UUID-based identification
    print("\n✅ UUID-Based Identification:")
    test_xml = """<APPLICATION-SW-COMPONENT-TYPE xmlns="http://autosar.org/schema/r4.0" 
                     UUID="test-uuid-123">
                    <SHORT-NAME>TestComponent</SHORT-NAME>
                  </APPLICATION-SW-COMPONENT-TYPE>"""
    
    element = etree.fromstring(test_xml.encode('utf-8'))
    uuid_value = handler.extract_split_key_value(element, "UUID")
    name_value = handler.extract_split_key_value(element, "SHORT-NAME")
    
    print(f"   UUID extraction: {uuid_value}")
    print(f"   SHORT-NAME extraction: {name_value}")
    print(f"   Primary identifier priority: {'✓' if uuid_value else '✗'}")


if __name__ == "__main__":
    demonstrate_partial_model_merge()
    test_standard_compliance()
    print("\n🎉 AUTOSAR Partial Model Merge demonstration completed!")