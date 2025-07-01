"""
Unit tests for the ARXML Merger
"""

import pytest
import tempfile
from pathlib import Path
from lxml import etree

from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy
from arxml_merger.core.exceptions import InvalidArxmlFileError, ArxmlMergerException
from arxml_merger.schema.autosar_schema import SchemaDetector


class TestArxmlMerger:
    """Test class for ArxmlMerger"""
    
    @pytest.fixture
    def sample_arxml1(self):
        """Creates a test ARXML file"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE>
            <SHORT-NAME>ComponentTypes</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE>
                    <SHORT-NAME>TestComponent1</SHORT-NAME>
                    <PORTS>
                        <P-PORT-PROTOTYPE>
                            <SHORT-NAME>Port1</SHORT-NAME>
                        </P-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""
    
    @pytest.fixture
    def sample_arxml2(self):
        """Creates a second test ARXML file"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <AR-PACKAGES>
        <AR-PACKAGE>
            <SHORT-NAME>ComponentTypes2</SHORT-NAME>
            <ELEMENTS>
                <APPLICATION-SW-COMPONENT-TYPE>
                    <SHORT-NAME>TestComponent2</SHORT-NAME>
                    <PORTS>
                        <R-PORT-PROTOTYPE>
                            <SHORT-NAME>Port2</SHORT-NAME>
                        </R-PORT-PROTOTYPE>
                    </PORTS>
                </APPLICATION-SW-COMPONENT-TYPE>
            </ELEMENTS>
        </AR-PACKAGE>
    </AR-PACKAGES>
</AUTOSAR>"""
    
    @pytest.fixture
    def temp_files(self, sample_arxml1, sample_arxml2):
        """Creates temporary files for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            file1 = temp_path / "test1.arxml"
            file2 = temp_path / "test2.arxml"
            
            file1.write_text(sample_arxml1, encoding='utf-8')
            file2.write_text(sample_arxml2, encoding='utf-8')
            
            yield [file1, file2], temp_path
    
    def test_basic_merge(self, temp_files):
        """Test basic merge functionality"""
        files, _ = temp_files
        
        merger = ArxmlMerger()
        result = merger.merge_files(files)
        
        assert result is not None
        assert result.statistics.files_processed == 2
        assert result.statistics.elements_merged > 0
        
        # Prüfe dass beide Komponenten im Ergebnis enthalten sind
        root = result.merged_tree
        components = []
        for element in root.iter():
            if etree.QName(element).localname == "APPLICATION-SW-COMPONENT-TYPE":
                components.append(element)
        
        component_names = []
        for comp in components:
            for child in comp.iter():
                if etree.QName(child).localname == "SHORT-NAME":
                    component_names.append(child.text)
                    break
        
        # Das Merge sollte beide Komponenten enthalten
        # Mit verschiedenen Package-Namen sollten beide Komponenten da sein
        assert len(components) == 2  # Beide Komponenten sollten vorhanden sein
        assert "TestComponent1" in component_names
        assert "TestComponent2" in component_names
    
    def test_save_result(self, temp_files):
        """Test Speichern des Merge-Ergebnisses"""
        files, temp_path = temp_files
        output_file = temp_path / "merged.arxml"
        
        merger = ArxmlMerger()
        result = merger.merge_files(files)
        result.save(output_file)
        
        assert output_file.exists()
        
        # Validiere gespeicherte Datei
        tree = etree.parse(str(output_file))
        root = tree.getroot()
        assert etree.QName(root).localname == "AUTOSAR"
    
    def test_invalid_file(self):
        """Test Behandlung ungültiger Dateien"""
        merger = ArxmlMerger()
        
        with pytest.raises((FileNotFoundError, InvalidArxmlFileError)):
            merger.merge_files(["nonexistent.arxml"])
    
    def test_empty_file_list(self):
        """Test leere Dateiliste"""
        merger = ArxmlMerger()
        
        with pytest.raises(ArxmlMergerException):
            merger.merge_files([])
    
    def test_conflict_resolution_strategies(self, temp_files):
        """Test verschiedene Konfliktauflösungsstrategien"""
        files, _ = temp_files
        
        # Test MERGE_ALL
        config = MergeConfig(conflict_resolution=ConflictResolutionStrategy.MERGE_ALL)
        merger = ArxmlMerger(config)
        result = merger.merge_files(files)
        assert result is not None
        
        # Test FIRST_WINS
        config = MergeConfig(conflict_resolution=ConflictResolutionStrategy.FIRST_WINS)
        merger = ArxmlMerger(config)
        result = merger.merge_files(files)
        assert result is not None


class TestSchemaDetector:
    """Test class for SchemaDetector"""
    
    def test_detect_schema_version(self):
        """Test Schema-Versionserkennung"""
        xml_content = """<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://autosar.org/schema/r4.0 autosar_r4.0.xsd">
</AUTOSAR>"""
        
        root = etree.fromstring(xml_content.encode('utf-8'))
        version = SchemaDetector.detect_schema_version(root)
        assert version == "4.0"
    
    def test_create_schema_handler(self):
        """Test Schema-Handler Erstellung"""
        handler = SchemaDetector.create_schema_handler("4.0")
        assert handler is not None
        assert handler.version == "4.0"
        assert "SW-COMPONENT-TYPE" in handler.split_keys


class TestErrorHandling:
    """Test class for Fehlerbehandlung"""
    
    def test_invalid_xml_content(self):
        """Test ungültiger XML-Inhalt"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            invalid_file = temp_path / "invalid.arxml"
            invalid_file.write_text("This is not XML", encoding='utf-8')
            
            merger = ArxmlMerger()
            with pytest.raises(InvalidArxmlFileError):
                merger.merge_files([invalid_file])
    
    def test_missing_autosar_root(self):
        """Test ARXML ohne AUTOSAR Root-Element"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            invalid_file = temp_path / "no_autosar.arxml"
            invalid_file.write_text(
                '<?xml version="1.0"?><ROOT><SOMETHING/></ROOT>', 
                encoding='utf-8'
            )
            
            merger = ArxmlMerger()
            with pytest.raises(InvalidArxmlFileError):
                merger.merge_files([invalid_file])


class TestMergeConfig:
    """Test class for MergeConfig"""
    
    def test_merge_config_defaults(self):
        """Test Standard-Konfiguration"""
        config = MergeConfig()
        assert config.conflict_resolution == ConflictResolutionStrategy.MERGE_ALL
        assert config.validate_schema == True
        assert config.preserve_comments == True
        assert config.output_encoding == "utf-8"
    
    def test_merge_config_custom(self):
        """Test benutzerdefinierte Konfiguration"""
        config = MergeConfig(
            conflict_resolution=ConflictResolutionStrategy.FIRST_WINS,
            validate_schema=False,
            preserve_comments=False,
            output_encoding="ascii"
        )
        assert config.conflict_resolution == ConflictResolutionStrategy.FIRST_WINS
        assert config.validate_schema == False
        assert config.preserve_comments == False
        assert config.output_encoding == "ascii"


class TestXmlUtils:
    """Test class for XML-Hilfsfunktionen"""
    
    def test_get_element_signature(self):
        """Test Element-Signatur-Erstellung"""
        from arxml_merger.utils.xml_utils import get_element_signature
        
        xml_content = """<APPLICATION-SW-COMPONENT-TYPE xmlns="http://autosar.org/schema/r4.0">
            <SHORT-NAME>TestComponent</SHORT-NAME>
        </APPLICATION-SW-COMPONENT-TYPE>"""
        
        element = etree.fromstring(xml_content.encode('utf-8'))
        signature = get_element_signature(element, ["SHORT-NAME"])
        assert "APPLICATION-SW-COMPONENT-TYPE" in signature
        assert "SHORT-NAME=TestComponent" in signature
    
    def test_validate_arxml_structure(self):
        """Test ARXML-Struktur-Validierung"""
        from arxml_merger.utils.xml_utils import validate_arxml_structure
        
        # Gültiges AUTOSAR
        valid_xml = """<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
            <AR-PACKAGES></AR-PACKAGES>
        </AUTOSAR>"""
        root = etree.fromstring(valid_xml.encode('utf-8'))
        errors = validate_arxml_structure(root)
        assert len(errors) == 0
        
        # Ungültiges Root-Element
        invalid_xml = """<NOT-AUTOSAR xmlns="http://autosar.org/schema/r4.0">
            <AR-PACKAGES></AR-PACKAGES>
        </NOT-AUTOSAR>"""
        root = etree.fromstring(invalid_xml.encode('utf-8'))
        errors = validate_arxml_structure(root)
        assert len(errors) > 0
        assert "Root-Element ist nicht 'AUTOSAR'" in errors


if __name__ == "__main__":
    pytest.main([__file__])
