"""
Data models for the ARXML Merger
"""

from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from lxml import etree


class ConflictResolutionStrategy(Enum):
    """Strategies for conflict resolution"""
    MERGE_ALL = "merge_all"           # Merge all values together
    FIRST_WINS = "first_wins"         # First value wins
    LAST_WINS = "last_wins"           # Last value wins
    MANUAL = "manual"                 # Manual resolution required
    FAIL_ON_CONFLICT = "fail"         # Fail on conflicts


@dataclass
class MergeConfig:
    """Configuration for the merge process"""
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.MERGE_ALL
    validate_schema: bool = True
    preserve_comments: bool = True
    preserve_formatting: bool = False
    output_encoding: str = "utf-8"
    verbose_merge: bool = False
    namespace_prefixes: Dict[str, str] = field(default_factory=dict)
    custom_split_keys: Dict[str, List[str]] = field(default_factory=dict)
    ignore_elements: List[str] = field(default_factory=list)


@dataclass
class MergeConflict:
    """Represents a merge conflict"""
    element_path: str
    attribute_name: Optional[str]
    conflicting_values: List[Any]
    source_files: List[str]
    resolution_strategy: Optional[ConflictResolutionStrategy] = None
    resolved_value: Optional[Any] = None


@dataclass
class MergeStatistics:
    """Statistics about the merge process"""
    files_processed: int = 0
    elements_merged: int = 0
    conflicts_found: int = 0
    conflicts_resolved: int = 0
    processing_time: float = 0.0
    schema_version: Optional[str] = None


class MergeResult:
    """Result of a merge process"""
    
    def __init__(self, 
                 merged_tree: etree._Element,
                 config: MergeConfig,
                 statistics: MergeStatistics,
                 conflicts: List[MergeConflict] = None):
        self.merged_tree = merged_tree
        self.config = config
        self.statistics = statistics
        self.conflicts = conflicts or []
        
    def save(self, output_path: Union[str, Path], pretty_print: bool = True) -> None:
        """Speichert das Merge-Ergebnis in eine Datei"""
        output_path = Path(output_path)
        
        # Stelle sicher, dass das Verzeichnis existiert
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Schreibe XML-Datei
        tree = etree.ElementTree(self.merged_tree)
        tree.write(
            str(output_path),
            encoding=self.config.output_encoding,
            xml_declaration=True,
            pretty_print=pretty_print
        )
    
    def to_string(self, pretty_print: bool = True) -> str:
        """Gibt das Merge-Ergebnis als String zurück"""
        return etree.tostring(
            self.merged_tree,
            encoding='unicode',
            pretty_print=pretty_print
        )
    
    def has_conflicts(self) -> bool:
        """Prüft ob noch ungelöste Konflikte existieren"""
        return any(conflict.resolved_value is None for conflict in self.conflicts)
    
    def get_unresolved_conflicts(self) -> List[MergeConflict]:
        """Gibt alle ungelösten Konflikte zurück"""
        return [conflict for conflict in self.conflicts if conflict.resolved_value is None]


@dataclass
class ArxmlFile:
    """Repräsentiert eine ARXML-Datei"""
    file_path: Path
    root_element: etree._Element
    schema_version: Optional[str] = None
    namespace_map: Dict[str, str] = field(default_factory=dict)
    split_keys: Dict[str, List[str]] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'ArxmlFile':
        """Lädt eine ARXML-Datei"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"ARXML-Datei nicht gefunden: {file_path}")
        
        # Parse XML
        parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
        tree = etree.parse(str(file_path), parser)
        root = tree.getroot()
        
        # Extrahiere Namespace-Map
        namespace_map = dict(root.nsmap)
        
        return cls(
            file_path=file_path,
            root_element=root,
            namespace_map=namespace_map
        )
