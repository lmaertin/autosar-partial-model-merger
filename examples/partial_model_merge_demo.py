"""
Comprehensive example demonstrating dSpace SystemDesk compatible merge functionality
"""

from pathlib import Path
import tempfile
from lxml import etree

from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy


def create_comprehensive_example():
    """Creates a comprehensive example showing dSpace SystemDesk compatible merge functionality"""
    
    # Base model with SHORT-NAME identifiers (like dSpace SystemDesk)
    base_model = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE>
            <SHORT-NAME>BaseSystem</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE>
                    <SHORT-NAME>EngineControl</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE>
                            <SHORT-NAME>ThrottlePosition</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                        <R-PORT-PROTOTYPE>
                            <SHORT-NAME>VehicleSpeed</SHORT-NAME>
                        </R-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
                <CLIENT-SERVER-INTERFACE>
                    <SHORT-NAME>DiagnosticInterface</SHORT-NAME>
                </CLIENT-SERVER-INTERFACE>
            </ELEMENTS>
        </AR-PACKAGE>
        <AR-PACKAGE>
            <SHORT-NAME>DataTypes</SHORT-NAME>
            <ELEMENTS>
                <IMPLEMENTATION-DATA-TYPE>
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
        <AR-PACKAGE>
            <SHORT-NAME>BaseSystem</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE>
                    <SHORT-NAME>EngineControl</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE>
                            <SHORT-NAME>EngineRPM</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                        <R-PORT-PROTOTYPE>
                            <SHORT-NAME>CoolantTemperature</SHORT-NAME>
                        </R-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
                <SENDER-RECEIVER-INTERFACE>
                    <SHORT-NAME>SensorInterface</SHORT-NAME>
                </SENDER-RECEIVER-INTERFACE>
            </ELEMENTS>
        </AR-PACKAGE>
        <AR-PACKAGE>
            <SHORT-NAME>AdaptiveApplications</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE>
                    <SHORT-NAME>AdaptiveService</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE>
                            <SHORT-NAME>ServicePort</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""

    # Third model with conflicting element (same SHORT-NAME, different content)
    conflict_model = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE>
            <SHORT-NAME>DataTypes</SHORT-NAME>
            <ELEMENTS>
                <IMPLEMENTATION-DATA-TYPE>
                    <SHORT-NAME>UInt32Type</SHORT-NAME>
                    <!-- This represents updated content for the same SHORT-NAME -->
                </IMPLEMENTATION-DATA-TYPE>
                <IMPLEMENTATION-DATA-TYPE>
                    <SHORT-NAME>Float64Type</SHORT-NAME>
                </IMPLEMENTATION-DATA-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""

    return base_model, extension_model, conflict_model


def demonstrate_partial_model_merge():
    """Demonstrates the dSpace SystemDesk compatible merge functionality"""
    
    print("dSpace SystemDesk Compatible Merge - Demo")
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
                "description": "Merging base model with extension using SHORT-NAME based identification"
            },
            {
                "name": "Three-Way Merge with Conflicts",
                "files": [base_file, extension_file, conflict_file],
                "strategy": ConflictResolutionStrategy.LAST_WINS,
                "description": "Merging three models with SHORT-NAME conflicts resolved by last-wins strategy"
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
    
    # Demonstrate SHORT-NAME based identification (like dSpace SystemDesk)
    short_name_elements = []
    for element in merged_tree.iter():
        for child in element:
            if etree.QName(child).localname == "SHORT-NAME" and child.text:
                short_name_elements.append((element, child.text))
                break
    
    print(f"     Elements with SHORT-NAME: {len(short_name_elements)}")
    
    # Show some sample SHORT-NAMEs
    if short_name_elements:
        print(f"     Sample SHORT-NAMEs:")
        for element, short_name in short_name_elements[:3]:
            tag = etree.QName(element).localname
            print(f"       {tag}: {short_name}")


def test_standard_compliance():
    """Tests specific dSpace SystemDesk compatible merge requirements"""
    
    print("\ndSpace SystemDesk Compatibility Tests")
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
    
    # Test SHORT-NAME based identification  
    print("\n✅ SHORT-NAME Based Identification:")
    test_xml = """<APPLICATION-SW-COMPONENT-TYPE xmlns="http://autosar.org/schema/r4.0">
                    <SHORT-NAME>TestComponent</SHORT-NAME>
                  </APPLICATION-SW-COMPONENT-TYPE>"""
    
    element = etree.fromstring(test_xml.encode('utf-8'))
    name_value = handler.extract_split_key_value(element, "SHORT-NAME")
    
    print(f"   SHORT-NAME extraction: {name_value}")
    print(f"   Primary identifier priority: {'✓' if name_value else '✗'}")


if __name__ == "__main__":
    demonstrate_partial_model_merge()
    test_standard_compliance()
    print("\n🎉 dSpace SystemDesk Compatible Merge demonstration completed!")