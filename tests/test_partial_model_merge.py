"""
Tests specifically for AUTOSAR Partial Model Merge standard compliance
"""

import pytest
import tempfile
from pathlib import Path
from lxml import etree

from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy
from arxml_merger.schema.autosar_schema import SchemaDetector
from arxml_merger.utils.xml_utils import get_element_signature, find_matching_element


class TestPartialModelMergeCompliance:
    """Test class for AUTOSAR Partial Model Merge standard compliance"""
    
    @pytest.fixture
    def base_arxml_with_short_names(self):
        """Creates a test ARXML file with SHORT-NAME identifiers like dSpace SystemDesk"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE>
            <SHORT-NAME>BaseComponents</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE>
                    <SHORT-NAME>BaseComponent</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE>
                            <SHORT-NAME>BasePort</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""
    
    @pytest.fixture
    def extension_arxml_with_short_names(self):
        """Creates an extension ARXML file using SHORT-NAME based identification"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE>
            <SHORT-NAME>BaseComponents</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE>
                    <SHORT-NAME>BaseComponent</SHORT-NAME>
                    <PORTS>
                        <R-PORT-PROTOTYPE>
                            <SHORT-NAME>ExtensionPort</SHORT-NAME>
                        </R-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""
    
    @pytest.fixture
    def temp_short_name_files(self, base_arxml_with_short_names, extension_arxml_with_short_names):
        """Creates temporary files with SHORT-NAME content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            file1 = temp_path / "base_short_name.arxml"
            file2 = temp_path / "extension_short_name.arxml"
            
            file1.write_text(base_arxml_with_short_names, encoding='utf-8')
            file2.write_text(extension_arxml_with_short_names, encoding='utf-8')
            
            yield [file1, file2], temp_path
    
    def test_short_name_based_element_matching(self):
        """Test that elements are matched primarily by SHORT-NAME like dSpace SystemDesk"""
        base_xml = """<APPLICATION-SW-COMPONENT-TYPE xmlns="http://autosar.org/schema/r4.0">
                        <SHORT-NAME>Component</SHORT-NAME>
                      </APPLICATION-SW-COMPONENT-TYPE>"""
        
        extension_xml = """<APPLICATION-SW-COMPONENT-TYPE xmlns="http://autosar.org/schema/r4.0">
                            <SHORT-NAME>Component</SHORT-NAME>
                           </APPLICATION-SW-COMPONENT-TYPE>"""
        
        base_element = etree.fromstring(base_xml.encode('utf-8'))
        extension_element = etree.fromstring(extension_xml.encode('utf-8'))
        
        # Test element signature with SHORT-NAME based approach
        signature_base = get_element_signature(base_element, ["SHORT-NAME"])
        signature_ext = get_element_signature(extension_element, ["SHORT-NAME"])
        
        # Should match when SHORT-NAME is the same
        assert "SHORT-NAME=Component" in signature_base
        assert "SHORT-NAME=Component" in signature_ext
        
        # Find matching should work
        matching = find_matching_element(base_element, [extension_element], ["SHORT-NAME"])
        assert matching is not None
    
    def test_splitable_elements_classification(self):
        """Test that splitable elements are correctly classified"""
        schema_handler = SchemaDetector.create_schema_handler("4.0")
        
        # Test that key splitable elements are recognized
        assert schema_handler.is_splitable_element("APPLICATION-SW-COMPONENT-TYPE")
        assert schema_handler.is_splitable_element("AR-PACKAGE")
        assert schema_handler.is_splitable_element("P-PORT-PROTOTYPE")
        assert schema_handler.is_splitable_element("CLIENT-SERVER-INTERFACE")
        assert schema_handler.is_splitable_element("IMPLEMENTATION-DATA-TYPE")
        
        # Test that non-splitable elements are not recognized as splitable
        assert not schema_handler.is_splitable_element("PORTS")
        assert not schema_handler.is_splitable_element("ELEMENTS")
        assert not schema_handler.is_splitable_element("INTERNAL-BEHAVIORS")
    
    def test_split_keys_use_short_name(self):
        """Test that splitable elements use SHORT-NAME as primary split key like dSpace SystemDesk"""
        schema_handler = SchemaDetector.create_schema_handler("4.0")
        
        # Test key splitable elements have SHORT-NAME as primary split key
        split_keys = schema_handler.get_element_split_keys("APPLICATION-SW-COMPONENT-TYPE")
        assert "SHORT-NAME" in split_keys
        assert split_keys[0] == "SHORT-NAME"  # SHORT-NAME should be first priority
        
        split_keys = schema_handler.get_element_split_keys("AR-PACKAGE")
        assert "SHORT-NAME" in split_keys
        assert split_keys[0] == "SHORT-NAME"
    
    def test_partial_model_merge_functionality(self, temp_short_name_files):
        """Test complete partial model merge with SHORT-NAME based matching like dSpace SystemDesk"""
        files, _ = temp_short_name_files
        
        merger = ArxmlMerger()
        result = merger.merge_files(files)
        
        # Should successfully merge
        assert result is not None
        assert result.statistics.files_processed == 2
        
        # Check that both ports are present in the merged result
        root = result.merged_tree
        ports = []
        for element in root.iter():
            if etree.QName(element).localname in ["P-PORT-PROTOTYPE", "R-PORT-PROTOTYPE"]:
                ports.append(element)
        
        # Should have both the base port and the extension port
        assert len(ports) == 2
        
        port_names = []
        for port in ports:
            for child in port:
                if etree.QName(child).localname == "SHORT-NAME":
                    port_names.append(child.text)
                    break
        
        assert "BasePort" in port_names
        assert "ExtensionPort" in port_names
    
    def test_short_name_extraction_methods(self):
        """Test different SHORT-NAME extraction patterns like dSpace SystemDesk"""
        schema_handler = SchemaDetector.create_schema_handler("4.0")
        
        # Test SHORT-NAME as child element
        xml_short_name_child = """<AR-PACKAGE xmlns="http://autosar.org/schema/r4.0">
                                    <SHORT-NAME>TestPackage</SHORT-NAME>
                                  </AR-PACKAGE>"""
        element = etree.fromstring(xml_short_name_child.encode('utf-8'))
        short_name_value = schema_handler.extract_split_key_value(element, "SHORT-NAME")
        assert short_name_value == "TestPackage"
        
        # Test SHORT-NAME as attribute (less common but possible)
        xml_short_name_attr = """<AR-PACKAGE xmlns="http://autosar.org/schema/r4.0" 
                                    SHORT-NAME="TestPackageAttr">
                                 </AR-PACKAGE>"""
        element = etree.fromstring(xml_short_name_attr.encode('utf-8'))
        short_name_value = schema_handler.extract_split_key_value(element, "SHORT-NAME")
        assert short_name_value == "TestPackageAttr"
    
    def test_partial_model_constraint_validation(self, temp_short_name_files):
        """Test validation of partial model constraints"""
        files, _ = temp_short_name_files
        
        merger = ArxmlMerger()
        
        # Should not raise exception for valid partial models
        try:
            result = merger.merge_files(files)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Valid partial models should not raise exception: {e}")
    
    def test_conflict_resolution_with_uuid_priority(self):
        """Test that conflict resolution respects UUID-based matching"""
        # Create elements with same UUID but different attributes
        base_xml = """<APPLICATION-SW-COMPONENT-TYPE xmlns="http://autosar.org/schema/r4.0" 
                         UUID="test-uuid-123" version="1.0">
                        <SHORT-NAME>Component</SHORT-NAME>
                      </APPLICATION-SW-COMPONENT-TYPE>"""
        
        extension_xml = """<APPLICATION-SW-COMPONENT-TYPE xmlns="http://autosar.org/schema/r4.0" 
                             UUID="test-uuid-123" version="2.0">
                            <SHORT-NAME>Component</SHORT-NAME>
                           </APPLICATION-SW-COMPONENT-TYPE>"""
        
        base_element = etree.fromstring(base_xml.encode('utf-8'))
        extension_element = etree.fromstring(extension_xml.encode('utf-8'))
        
        # Elements should match based on UUID despite different version attributes
        matching = find_matching_element(base_element, [extension_element], ["UUID", "SHORT-NAME"])
        assert matching is not None
        assert matching.get("UUID") == "test-uuid-123"


class TestAutosarSchemaHandlerEnhancements:
    """Test enhancements to AUTOSAR schema handlers"""
    
    def test_schema_handler_uuid_support(self):
        """Test that schema handlers properly support UUID extraction"""
        for version in ["4.0", "4.3.1", "4.4", "20-11", "24-11"]:
            handler = SchemaDetector.create_schema_handler(version)
            
            # Create test element with UUID
            xml_content = f"""<APPLICATION-SW-COMPONENT-TYPE 
                                xmlns="{handler.namespace_uri}" 
                                UUID="test-uuid-456">
                                <SHORT-NAME>TestComp</SHORT-NAME>
                              </APPLICATION-SW-COMPONENT-TYPE>"""
            
            element = etree.fromstring(xml_content.encode('utf-8'))
            
            # Test UUID extraction
            uuid_value = handler.extract_split_key_value(element, "UUID")
            assert uuid_value == "test-uuid-456"
            
            # Test SHORT-NAME extraction
            name_value = handler.extract_split_key_value(element, "SHORT-NAME")
            assert name_value == "TestComp"
    
    def test_short_name_based_split_key_logic(self):
        """Test that SHORT-NAME based split key logic works correctly like dSpace SystemDesk"""
        handler = SchemaDetector.create_schema_handler("4.0")
        
        # Test that splitable elements get SHORT-NAME as primary split key
        split_keys = handler.get_element_split_keys("APPLICATION-SW-COMPONENT-TYPE")
        assert len(split_keys) >= 1
        assert split_keys[0] == "SHORT-NAME"


if __name__ == "__main__":
    pytest.main([__file__])