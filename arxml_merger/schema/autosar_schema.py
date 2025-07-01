"""
Schema-specific implementations for AUTOSAR versions

Supported AUTOSAR versions (4.3.1 to 24-11):
- 4.0.x, 4.1.x, 4.2.x (legacy versions - basic support)
- 4.3.1+ (minimum recommended version - full feature support)
- 4.4.x (last of the 4.x series)
- 20-11, 21-11, 22-11, 23-11, 24-11 (modern AUTOSAR releases)

Note: AUTOSAR 4.5 does not exist. The series jumped from 4.4 to the new 
year-month naming convention starting with 20-11.
"""

from typing import Dict, List, Set, Optional, Tuple
from abc import ABC, abstractmethod
from lxml import etree
import re


class AutosarSchemaHandler(ABC):
    """Abstract base class for AUTOSAR Schema Handlers"""
    
    def __init__(self, version: str):
        self.version = version
        self.namespace_uri = self._get_namespace_uri()
        self.split_keys = self._get_split_keys()
        self.splitable_elements = self._get_splitable_elements()
    
    @abstractmethod
    def _get_namespace_uri(self) -> str:
        """Returns the namespace URI for this schema version"""
        pass
    
    @abstractmethod
    def _get_split_keys(self) -> Dict[str, List[str]]:
        """Returns the split keys for this schema version"""
        pass
    
    @abstractmethod
    def _get_splitable_elements(self) -> Set[str]:
        """Returns the splitable elements for this schema version"""
        pass
    
    def is_splitable_element(self, element_name: str) -> bool:
        """Checks if an element is splitable"""
        return element_name in self.splitable_elements
    
    def get_element_split_keys(self, element_name: str) -> List[str]:
        """Returns the split keys for an element"""
        return self.split_keys.get(element_name, [])
    
    def extract_split_key_value(self, element: etree._Element, split_key: str) -> Optional[str]:
        """Extracts the value of a split key from an element"""
        # Try as attribute first
        if element.get(split_key):
            return element.get(split_key)
        
        # Then as child element
        child = element.find(f".//{{{self.namespace_uri}}}{split_key}")
        if child is not None and child.text:
            return child.text.strip()
        
        return None


class Autosar40SchemaHandler(AutosarSchemaHandler):
    """Schema Handler für AUTOSAR 4.0.x"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"
    
    def _get_split_keys(self) -> Dict[str, List[str]]:
        return {
            "SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "APPLICATION-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "COMPOSITION-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "ECU-ABSTRACTION-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "SERVICE-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "SENSOR-ACTUATOR-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "PARAMETER-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "CALIBRATION-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "PORT-PROTOTYPE": ["SHORT-NAME"],
            "P-PORT-PROTOTYPE": ["SHORT-NAME"],
            "R-PORT-PROTOTYPE": ["SHORT-NAME"],
            "PR-PORT-PROTOTYPE": ["SHORT-NAME"],
            "RUNNABLE-ENTITY": ["SHORT-NAME"],
            "VARIABLE-DATA-PROTOTYPE": ["SHORT-NAME"],
            "PARAMETER-DATA-PROTOTYPE": ["SHORT-NAME"],
            "ARGUMENT-DATA-PROTOTYPE": ["SHORT-NAME"],
            "OPERATION-PROTOTYPE": ["SHORT-NAME"],
            "CLIENT-SERVER-INTERFACE": ["SHORT-NAME"],
            "SENDER-RECEIVER-INTERFACE": ["SHORT-NAME"],
            "NV-DATA-INTERFACE": ["SHORT-NAME"],
            "PARAMETER-INTERFACE": ["SHORT-NAME"],
            "MODE-SWITCH-INTERFACE": ["SHORT-NAME"],
            "TRIGGER-INTERFACE": ["SHORT-NAME"],
            "DATA-TYPE-MAPPING": ["SHORT-NAME"],
            "IMPLEMENTATION-DATA-TYPE": ["SHORT-NAME"],
            "APPLICATION-PRIMITIVE-DATA-TYPE": ["SHORT-NAME"],
            "APPLICATION-RECORD-DATA-TYPE": ["SHORT-NAME"],
            "APPLICATION-ARRAY-DATA-TYPE": ["SHORT-NAME"],
            "AUTOSAR-DATA-TYPE": ["SHORT-NAME"],
            "UNIT": ["SHORT-NAME"],
            "COMPU-METHOD": ["SHORT-NAME"],
            "DATA-CONSTR": ["SHORT-NAME"],
            "CONSTANT-SPECIFICATION": ["SHORT-NAME"],
            "SYSTEM": ["SHORT-NAME"],
            "ECU-INSTANCE": ["SHORT-NAME"],
            "CAN-CLUSTER": ["SHORT-NAME"],
            "CAN-FRAME": ["SHORT-NAME"],
            "I-PDU": ["SHORT-NAME"],
            "I-SIGNAL": ["SHORT-NAME"],
            "SYSTEM-SIGNAL": ["SHORT-NAME"],
            "FIBEX-ELEMENT": ["SHORT-NAME"],
            "CATEGORY": ["SHORT-NAME"],
            "PACKAGE": ["SHORT-NAME"],
            "AR-PACKAGE": ["SHORT-NAME"],
        }
    
    def _get_splitable_elements(self) -> Set[str]:
        return {
            "SW-COMPONENT-TYPE",
            "APPLICATION-SW-COMPONENT-TYPE",
            "COMPOSITION-SW-COMPONENT-TYPE",
            "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE",
            "ECU-ABSTRACTION-SW-COMPONENT-TYPE",
            "SERVICE-SW-COMPONENT-TYPE",
            "SENSOR-ACTUATOR-SW-COMPONENT-TYPE",
            "PARAMETER-SW-COMPONENT-TYPE",
            "CALIBRATION-SW-COMPONENT-TYPE",
            "PORT-PROTOTYPE",
            "P-PORT-PROTOTYPE",
            "R-PORT-PROTOTYPE",
            "PR-PORT-PROTOTYPE",
            "RUNNABLE-ENTITY",
            "VARIABLE-DATA-PROTOTYPE",
            "PARAMETER-DATA-PROTOTYPE",
            "ARGUMENT-DATA-PROTOTYPE",
            "OPERATION-PROTOTYPE",
            "CLIENT-SERVER-INTERFACE",
            "SENDER-RECEIVER-INTERFACE",
            "NV-DATA-INTERFACE",
            "PARAMETER-INTERFACE",
            "MODE-SWITCH-INTERFACE",
            "TRIGGER-INTERFACE",
            "IMPLEMENTATION-DATA-TYPE",
            "APPLICATION-PRIMITIVE-DATA-TYPE",
            "APPLICATION-RECORD-DATA-TYPE",
            "APPLICATION-ARRAY-DATA-TYPE",
            "AUTOSAR-DATA-TYPE",
            "UNIT",
            "COMPU-METHOD",
            "DATA-CONSTR",
            "CONSTANT-SPECIFICATION",
            "SYSTEM",
            "ECU-INSTANCE",
            "CAN-CLUSTER",
            "CAN-FRAME",
            "I-PDU",
            "I-SIGNAL",
            "SYSTEM-SIGNAL",
            "FIBEX-ELEMENT",
            "CATEGORY",
            "PACKAGE",
            "AR-PACKAGE",
        }


class Autosar41SchemaHandler(Autosar40SchemaHandler):
    """Schema Handler für AUTOSAR 4.1.x"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"  # 4.1 verwendet oft dieselbe Namespace


class Autosar42SchemaHandler(Autosar40SchemaHandler):
    """Schema Handler für AUTOSAR 4.2.x"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"
    
    def _get_split_keys(self) -> Dict[str, List[str]]:
        split_keys = super()._get_split_keys()
        # Extend with 4.2-specific split keys
        split_keys.update({
            "ADAPTIVE-APPLICATION-SW-COMPONENT-TYPE": ["SHORT-NAME"],
            "SERVICE-INTERFACE": ["SHORT-NAME"],
            "SOMEIP-SERVICE-INTERFACE": ["SHORT-NAME"],
            "PERSISTENCY-INTERFACE": ["SHORT-NAME"],
        })
        return split_keys
    
    def _get_splitable_elements(self) -> Set[str]:
        elements = super()._get_splitable_elements()
        # Extend with 4.2-specific elements
        elements.update({
            "ADAPTIVE-APPLICATION-SW-COMPONENT-TYPE",
            "SERVICE-INTERFACE",
            "SOMEIP-SERVICE-INTERFACE",
            "PERSISTENCY-INTERFACE",
        })
        return elements


class Autosar431SchemaHandler(Autosar42SchemaHandler):
    """Schema Handler for AUTOSAR 4.3.1+"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"


class Autosar44SchemaHandler(Autosar431SchemaHandler):
    """Schema Handler for AUTOSAR 4.4.x (last of 4.x series)"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"


class Autosar2011SchemaHandler(Autosar44SchemaHandler):
    """Schema Handler for AUTOSAR 20-11"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"


class Autosar2111SchemaHandler(Autosar2011SchemaHandler):
    """Schema Handler for AUTOSAR 21-11"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"


class Autosar2211SchemaHandler(Autosar2111SchemaHandler):
    """Schema Handler for AUTOSAR 22-11"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"


class Autosar2311SchemaHandler(Autosar2211SchemaHandler):
    """Schema Handler for AUTOSAR 23-11"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"


class Autosar2411SchemaHandler(Autosar2311SchemaHandler):
    """Schema Handler for AUTOSAR 24-11 (latest)"""
    
    def _get_namespace_uri(self) -> str:
        return "http://autosar.org/schema/r4.0"


class SchemaDetector:
    """Detects AUTOSAR schema versions from ARXML files"""
    
    @staticmethod
    def detect_schema_version(root_element: etree._Element) -> str:
        """Detects the schema version from the root element"""
        # Check schema location
        schema_location = root_element.get("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation")
        if schema_location:
            # Extract version from schema location - handle new format (20-11, 21-11, etc.)
            new_format_match = re.search(r'(\d{2})-(\d{2})', schema_location)
            if new_format_match:
                year, month = new_format_match.groups()
                return f"{year}-{month}"
            
            # Extract version from schema location - old format (r4.x)
            version_match = re.search(r'r(\d+)\.(\d+)', schema_location)
            if version_match:
                major, minor = version_match.groups()
                return f"{major}.{minor}"
        
        # Check namespace URI
        namespace = root_element.nsmap.get(None)
        if namespace:
            # Check for new format versions in namespace
            if "24-11" in namespace or "2411" in namespace:
                return "24-11"
            elif "23-11" in namespace or "2311" in namespace:
                return "23-11"
            elif "22-11" in namespace or "2211" in namespace:
                return "22-11"
            elif "21-11" in namespace or "2111" in namespace:
                return "21-11"
            elif "20-11" in namespace or "2011" in namespace:
                return "20-11"
            # Check for old format versions
            elif "r4.4" in namespace:
                return "4.4"
            elif "r4.3" in namespace:
                return "4.3.1"  # Start at 4.3.1 as requested
            elif "r4.2" in namespace:
                return "4.2"
            elif "r4.1" in namespace:
                return "4.1"
            elif "r4.0" in namespace:
                return "4.0"
        
        # Fallback: Check specific elements for adaptive platform features
        for element in root_element.iter():
            if etree.QName(element).localname == "ADAPTIVE-APPLICATION-SW-COMPONENT-TYPE":
                return "4.3.1"  # At least 4.3.1 for adaptive platform
        
        # Default to earliest supported version
        return "4.3.1"
    
    @staticmethod
    def create_schema_handler(version: str) -> AutosarSchemaHandler:
        """Creates a schema handler for the given version"""
        handlers = {
            "4.0": Autosar40SchemaHandler,
            "4.1": Autosar41SchemaHandler,
            "4.2": Autosar42SchemaHandler,
            "4.3.1": Autosar431SchemaHandler,
            "4.4": Autosar44SchemaHandler,
            "20-11": Autosar2011SchemaHandler,
            "21-11": Autosar2111SchemaHandler,
            "22-11": Autosar2211SchemaHandler,
            "23-11": Autosar2311SchemaHandler,
            "24-11": Autosar2411SchemaHandler,
        }
        
        # Use the most appropriate handler, fallback to 4.3.1 as minimum
        handler_class = handlers.get(version, Autosar431SchemaHandler)
        return handler_class(version)
