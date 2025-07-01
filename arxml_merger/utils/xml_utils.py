"""
Hilfsfunktionen für den ARXML Merger
"""

from typing import List, Optional
from lxml import etree
from pathlib import Path
import hashlib
import logging


def get_element_path(element: etree._Element, root: etree._Element = None) -> str:
    """Erstellt einen eindeutigen Pfad für ein XML-Element"""
    if root is None:
        root = element.getroottree().getroot()
    
    path_parts = []
    current = element
    
    while current is not None and current != root:
        # Erstelle Elementname mit Index falls mehrere gleichnamige Geschwister
        tag_name = etree.QName(current).localname
        siblings = list(current.getparent()) if current.getparent() is not None else []
        same_tag_siblings = [s for s in siblings if etree.QName(s).localname == tag_name]
        
        if len(same_tag_siblings) > 1:
            index = same_tag_siblings.index(current) + 1
            path_parts.append(f"{tag_name}[{index}]")
        else:
            path_parts.append(tag_name)
        
        current = current.getparent()
    
    path_parts.reverse()
    return "/" + "/".join(path_parts)


def get_element_signature(element: etree._Element, split_keys: List[str] = None) -> str:
    """Erstellt eine eindeutige Signatur für ein Element basierend auf Split-Keys"""
    if not split_keys:
        split_keys = ["SHORT-NAME"]
    
    signature_parts = [etree.QName(element).localname]
    
    for key in split_keys:
        value = None
        
        # Prüfe Attribut
        if element.get(key):
            value = element.get(key)
        else:
            # Prüfe Kinder-Element - einfachere Suche
            child = None
            for c in element:
                if etree.QName(c).localname == key:
                    child = c
                    break
            if child is not None and child.text:
                value = child.text.strip()
        
        if value:
            signature_parts.append(f"{key}={value}")
    
    return "|".join(signature_parts)


def find_matching_element(target_element: etree._Element, 
                         source_elements: List[etree._Element], 
                         split_keys: List[str] = None) -> Optional[etree._Element]:
    """Findet ein passendes Element in einer Liste basierend auf Split-Keys"""
    target_signature = get_element_signature(target_element, split_keys)
    
    for source_element in source_elements:
        if get_element_signature(source_element, split_keys) == target_signature:
            return source_element
    
    return None


def merge_attributes(target: etree._Element, 
                    source: etree._Element, 
                    conflict_strategy: str = "merge") -> List[str]:
    """Merged Attribute zwischen zwei Elementen"""
    conflicts = []
    
    for attr_name, attr_value in source.attrib.items():
        if attr_name in target.attrib:
            if target.attrib[attr_name] != attr_value:
                # Konflikt erkannt
                conflicts.append(f"Attribut '{attr_name}': '{target.attrib[attr_name]}' vs '{attr_value}'")
                
                if conflict_strategy == "source_wins":
                    target.set(attr_name, attr_value)
                elif conflict_strategy == "target_wins":
                    pass  # Behalte den Zielwert
                # Bei "merge" oder anderen Strategien bleibt der ursprüngliche Wert
        else:
            # Neues Attribut hinzufügen
            target.set(attr_name, attr_value)
    
    return conflicts


def normalize_whitespace(text: str) -> str:
    """Normalisiert Whitespace in Text"""
    if not text:
        return ""
    return " ".join(text.split())


def create_element_hash(element: etree._Element) -> str:
    """Erstellt einen Hash für ein Element basierend auf seinem Inhalt"""
    content = etree.tostring(element, encoding='unicode', method='xml')
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def validate_arxml_structure(root_element: etree._Element) -> List[str]:
    """Validiert die grundlegende ARXML-Struktur"""
    errors = []
    
    # Prüfe Root-Element
    if etree.QName(root_element).localname != "AUTOSAR":
        errors.append("Root-Element ist nicht 'AUTOSAR'")
    
    # Prüfe Namespace
    if not root_element.nsmap:
        errors.append("Keine Namespace-Deklaration gefunden")
    
    # Prüfe AR-PACKAGES - einfachere Suche
    ar_packages = None
    for child in root_element:
        if etree.QName(child).localname == "AR-PACKAGES":
            ar_packages = child
            break
    
    if ar_packages is None:
        errors.append("Keine AR-PACKAGES gefunden")
    
    return errors


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> logging.Logger:
    """Richtet Logging für den Merger ein"""
    logger = logging.getLogger("arxml_merger")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Entferne bestehende Handler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def deep_copy_element(element: etree._Element) -> etree._Element:
    """Erstellt eine tiefe Kopie eines XML-Elements"""
    # Konvertiere zu String und parse wieder für echte Deep Copy
    xml_string = etree.tostring(element, encoding='unicode')
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.fromstring(xml_string, parser)


def get_namespace_prefix(element: etree._Element, namespace_uri: str) -> Optional[str]:
    """Findet das Präfix für eine Namespace-URI"""
    nsmap = element.nsmap
    for prefix, uri in nsmap.items():
        if uri == namespace_uri:
            return prefix
    return None


def remove_empty_elements(root: etree._Element) -> int:
    """Entfernt leere Elemente aus dem Baum"""
    removed_count = 0
    
    # Arbeite von unten nach oben (Kinder zuerst)
    for element in root.iter():
        # Sammle Kinder zum Entfernen
        children_to_remove = []
        for child in element:
            if (not child.text or child.text.strip() == "") and \
               len(child) == 0 and \
               not child.attrib:
                children_to_remove.append(child)
        
        # Entferne leere Kinder
        for child in children_to_remove:
            element.remove(child)
            removed_count += 1
    
    return removed_count


def format_xml_pretty(element: etree._Element, indent: str = "  ") -> None:
    """Formatiert XML für schöne Ausgabe"""
    def _indent(elem, level=0):
        i = "\n" + level * indent
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + indent
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                _indent(child, level + 1)
            if len(elem) > 0:
                if not elem[-1].tail or not elem[-1].tail.strip():
                    elem[-1].tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    _indent(element)


def get_autosar_path(element: etree._Element, root: etree._Element = None) -> str:
    """Erstellt einen AUTOSAR-spezifischen Pfad mit SHORT-NAME Elementen"""
    if root is None:
        root = element.getroottree().getroot()
    
    path_parts = []
    current = element
    
    while current is not None and current != root:
        tag_name = etree.QName(current).localname
        
        # Versuche SHORT-NAME zu finden
        short_name = None
        for child in current:
            if etree.QName(child).localname == "SHORT-NAME":
                short_name = child.text.strip() if child.text else None
                break
        
        if short_name:
            path_parts.append(f"{tag_name}[{short_name}]")
        else:
            # Fallback auf Index wenn kein SHORT-NAME vorhanden
            siblings = list(current.getparent()) if current.getparent() is not None else []
            same_tag_siblings = [s for s in siblings if etree.QName(s).localname == tag_name]
            
            if len(same_tag_siblings) > 1:
                index = same_tag_siblings.index(current) + 1
                path_parts.append(f"{tag_name}[{index}]")
            else:
                path_parts.append(tag_name)
        
        current = current.getparent()
    
    path_parts.reverse()
    return "/" + "/".join(path_parts)
