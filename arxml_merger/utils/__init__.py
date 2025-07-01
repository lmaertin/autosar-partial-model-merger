"""
__init__.py für utils Modul
"""

from .xml_utils import (
    get_element_path,
    get_element_signature,
    find_matching_element,
    merge_attributes,
    normalize_whitespace,
    create_element_hash,
    validate_arxml_structure,
    setup_logging,
    deep_copy_element,
    get_namespace_prefix,
    remove_empty_elements,
    format_xml_pretty
)

__all__ = [
    "get_element_path",
    "get_element_signature", 
    "find_matching_element",
    "merge_attributes",
    "normalize_whitespace",
    "create_element_hash",
    "validate_arxml_structure",
    "setup_logging",
    "deep_copy_element",
    "get_namespace_prefix",
    "remove_empty_elements",
    "format_xml_pretty"
]
