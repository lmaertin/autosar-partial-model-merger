"""
Hauptklasse für das Mergen von AUTOSAR ARXML-Dateien
"""

from typing import List, Union, Optional, Dict
from pathlib import Path
import time
import logging

from lxml import etree

from ..core.models import (
    MergeConfig, MergeResult, MergeStatistics, MergeConflict, 
    ConflictResolutionStrategy, ArxmlFile
)
from ..core.exceptions import (
    ArxmlMergerException, InvalidArxmlFileError, MergeConflictError, SplitKeyError
)
from ..schema.autosar_schema import SchemaDetector, AutosarSchemaHandler
from ..utils.xml_utils import (
    get_element_path, get_element_signature, find_matching_element,
    merge_attributes, validate_arxml_structure, deep_copy_element,
    setup_logging
)


class ArxmlMerger:
    """Hauptklasse für das Mergen von AUTOSAR ARXML-Dateien"""
    
    def __init__(self, config: Optional[MergeConfig] = None):
        """
        Initialisiert den ARXML Merger
        
        Args:
            config: Konfiguration für den Merge-Prozess
        """
        self.config = config or MergeConfig()
        self.logger = setup_logging()
        self.schema_handlers: Dict[str, AutosarSchemaHandler] = {}
        
    def merge_files(self, file_paths: List[Union[str, Path]]) -> MergeResult:
        """
        Merged mehrere ARXML-Dateien
        
        Args:
            file_paths: Liste der zu mergenden Dateien
            
        Returns:
            MergeResult mit dem Ergebnis des Merge-Prozesses
        """
        start_time = time.time()
        
        if not file_paths:
            raise ArxmlMergerException("No files provided for merging")
        
        self.logger.info("Starting merge process for %d files", len(file_paths))
        
        # Lade alle Dateien
        arxml_files = []
        for file_path in file_paths:
            try:
                arxml_file = ArxmlFile.from_file(file_path)
                arxml_file.schema_version = SchemaDetector.detect_schema_version(arxml_file.root_element)
                arxml_files.append(arxml_file)
                self.logger.info("File loaded: %s (Schema: %s)", file_path, arxml_file.schema_version)
            except Exception as e:
                raise InvalidArxmlFileError(f"Error loading file {file_path}: {e}", str(file_path)) from e
        
        # Validiere Dateien
        self._validate_files(arxml_files)
        
        # Führe Merge durch
        merged_tree, conflicts = self._merge_arxml_files(arxml_files)
        
        # Erstelle Statistiken
        processing_time = time.time() - start_time
        statistics = MergeStatistics(
            files_processed=len(file_paths),
            elements_merged=self._count_elements(merged_tree),
            conflicts_found=len(conflicts),
            conflicts_resolved=len([c for c in conflicts if c.resolved_value is not None]),
            processing_time=processing_time,
            schema_version=arxml_files[0].schema_version if arxml_files else None
        )
        
        self.logger.info("Merge completed in %.2fs", processing_time)
        self.logger.info("Elements merged: %d", statistics.elements_merged)
        self.logger.info("Conflicts found: %d", statistics.conflicts_found)
        
        return MergeResult(merged_tree, self.config, statistics, conflicts)
    
    def _validate_files(self, files: List[ArxmlFile]) -> None:
        """Validiert die ARXML-Dateien vor dem Merge"""
        schema_versions = set(f.schema_version for f in files)
        
        if len(schema_versions) > 1:
            self.logger.warning("Different schema versions detected: %s", schema_versions)
        
        for arxml_file in files:
            errors = validate_arxml_structure(arxml_file.root_element)
            if errors:
                raise InvalidArxmlFileError(
                    f"Strukturfehler in {arxml_file.file_path}: {errors}",
                    str(arxml_file.file_path)
                )
    
    def _merge_arxml_files(self, files: List[ArxmlFile]) -> tuple[etree._Element, List[MergeConflict]]:
        """Führt den eigentlichen Merge der ARXML-Dateien durch"""
        if not files:
            raise ArxmlMergerException("Keine Dateien zum Mergen")
        
        # Verwende die erste Datei als Basis
        base_file = files[0]
        merged_root = deep_copy_element(base_file.root_element)
        
        # Hole Schema-Handler für die Hauptversion
        schema_handler = self._get_schema_handler(base_file.schema_version)
        
        conflicts = []
        
        # Merge jede weitere Datei
        for i, source_file in enumerate(files[1:], 1):
            self.logger.info("Merging file %d/%d: %s", i+1, len(files), source_file.file_path)
            
            source_conflicts = self._merge_single_file(
                merged_root, 
                source_file.root_element, 
                schema_handler,
                str(source_file.file_path)
            )
            conflicts.extend(source_conflicts)
        
        return merged_root, conflicts
    
    def _merge_single_file(self, 
                          target_root: etree._Element, 
                          source_root: etree._Element,
                          schema_handler: AutosarSchemaHandler,
                          source_file_path: str) -> List[MergeConflict]:
        """Merged eine einzelne Datei in den Zielbaum"""
        conflicts = []
        
        # Merge AR-PACKAGES - einfachere Suche
        target_packages = None
        source_packages = None
        
        for child in target_root:
            if etree.QName(child).localname == "AR-PACKAGES":
                target_packages = child
                break
                
        for child in source_root:
            if etree.QName(child).localname == "AR-PACKAGES":
                source_packages = child
                break
        
        if target_packages is None or source_packages is None:
            self.logger.warning("AR-PACKAGES not found")
            return conflicts
        
        # Merge Packages rekursiv
        package_conflicts = self._merge_packages(
            target_packages, source_packages, schema_handler, source_file_path
        )
        conflicts.extend(package_conflicts)
        
        return conflicts
    
    def _merge_packages(self, 
                       target_packages: etree._Element, 
                       source_packages: etree._Element,
                       schema_handler: AutosarSchemaHandler,
                       source_file_path: str) -> List[MergeConflict]:
        """Merged AR-PACKAGE Elemente"""
        conflicts = []
        
        # Alle AR-PACKAGE Elemente der Quelle - einfachere Suche
        source_package_elements = []
        for child in source_packages:
            if etree.QName(child).localname == "AR-PACKAGE":
                source_package_elements.append(child)
        
        for source_package in source_package_elements:
            conflicts.extend(self._merge_package(
                target_packages, source_package, schema_handler, source_file_path
            ))
        
        return conflicts
    
    def _merge_package(self, 
                      target_packages: etree._Element, 
                      source_package: etree._Element,
                      schema_handler: AutosarSchemaHandler,
                      source_file_path: str) -> List[MergeConflict]:
        """Merged ein einzelnes AR-PACKAGE"""
        conflicts = []
        
        # Finde passendes Package im Ziel
        split_keys = schema_handler.get_element_split_keys("AR-PACKAGE")
        target_package_elements = []
        for child in target_packages:
            if etree.QName(child).localname == "AR-PACKAGE":
                target_package_elements.append(child)
        
        matching_package = find_matching_element(
            source_package, target_package_elements, split_keys
        )
        
        if matching_package is None:
            # Neues Package hinzufügen
            new_package = deep_copy_element(source_package)
            target_packages.append(new_package)
            self.logger.debug("New package added: %s", get_element_signature(source_package, split_keys))
        else:
            # Package mergen
            conflicts.extend(self._merge_elements(
                matching_package, source_package, schema_handler, source_file_path
            ))
        
        return conflicts
    
    def _merge_elements(self, 
                       target_element: etree._Element, 
                       source_element: etree._Element,
                       schema_handler: AutosarSchemaHandler,
                       source_file_path: str) -> List[MergeConflict]:
        """Merged zwei Elemente rekursiv"""
        conflicts = []
        
        # Merge Attribute
        attr_conflicts = merge_attributes(
            target_element, source_element, 
            "source_wins" if self.config.conflict_resolution == ConflictResolutionStrategy.LAST_WINS else "target_wins"
        )
        
        for attr_conflict in attr_conflicts:
            conflicts.append(MergeConflict(
                element_path=get_element_path(target_element),
                attribute_name=None,  # Wird im Konflikt-String beschrieben
                conflicting_values=[attr_conflict],
                source_files=[source_file_path]
            ))
        
        # Merge Kinder-Elemente
        element_name = etree.QName(target_element).localname
        
        if schema_handler.is_splitable_element(element_name):
            # Verwende Split-Keys für splitbare Elemente
            split_keys = schema_handler.get_element_split_keys(element_name)
            child_conflicts = self._merge_splitable_children(
                target_element, source_element, split_keys, schema_handler, source_file_path
            )
            conflicts.extend(child_conflicts)
        else:
            # Standard-Merge für andere Elemente
            child_conflicts = self._merge_standard_children(
                target_element, source_element, schema_handler, source_file_path
            )
            conflicts.extend(child_conflicts)
        
        return conflicts
    
    def _merge_splitable_children(self, 
                                 target_element: etree._Element, 
                                 source_element: etree._Element,
                                 split_keys: List[str],
                                 schema_handler: AutosarSchemaHandler,
                                 source_file_path: str) -> List[MergeConflict]:
        """Merged Kinder von splitbaren Elementen"""
        conflicts = []
        
        # Gruppiere Kinder nach Tag-Namen
        source_children_by_tag = {}
        for child in source_element:
            tag = etree.QName(child).localname
            if tag not in source_children_by_tag:
                source_children_by_tag[tag] = []
            source_children_by_tag[tag].append(child)
        
        for tag, source_children in source_children_by_tag.items():
            target_children = [c for c in target_element if etree.QName(c).localname == tag]
            
            for source_child in source_children:
                matching_child = find_matching_element(source_child, target_children, split_keys)
                
                if matching_child is None:
                    # Neues Element hinzufügen
                    new_child = deep_copy_element(source_child)
                    target_element.append(new_child)
                else:
                    # Element mergen
                    conflicts.extend(self._merge_elements(
                        matching_child, source_child, schema_handler, source_file_path
                    ))
        
        return conflicts
    
    def _merge_standard_children(self, 
                                target_element: etree._Element, 
                                source_element: etree._Element,
                                schema_handler: AutosarSchemaHandler,
                                source_file_path: str) -> List[MergeConflict]:
        """Merged Kinder von nicht-splitbaren Elementen"""
        conflicts = []
        
        # Einfache Strategie: Füge alle Kinder hinzu, die nicht bereits existieren
        for source_child in source_element:
            source_tag = etree.QName(source_child).localname
            
            # Prüfe ob bereits ein Kind mit diesem Tag existiert
            existing_child = None
            for child in target_element:
                if etree.QName(child).localname == source_tag:
                    existing_child = child
                    break
            
            if existing_child is None:
                # Neues Kind hinzufügen
                new_child = deep_copy_element(source_child)
                target_element.append(new_child)
            else:
                # Konflikt oder rekursiver Merge
                if self.config.conflict_resolution == ConflictResolutionStrategy.FAIL_ON_CONFLICT:
                    conflicts.append(MergeConflict(
                        element_path=get_element_path(existing_child),
                        attribute_name=None,
                        conflicting_values=[existing_child.text, source_child.text],
                        source_files=[source_file_path]
                    ))
                else:
                    # Rekursiver Merge
                    conflicts.extend(self._merge_elements(
                        existing_child, source_child, schema_handler, source_file_path
                    ))
        
        return conflicts
    
    def _get_schema_handler(self, version: str) -> AutosarSchemaHandler:
        """Holt oder erstellt einen Schema-Handler für die Version"""
        if version not in self.schema_handlers:
            self.schema_handlers[version] = SchemaDetector.create_schema_handler(version)
        return self.schema_handlers[version]
    
    def _count_elements(self, root: etree._Element) -> int:
        """Zählt alle Elemente im Baum"""
        return len(list(root.iter()))
