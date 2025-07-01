"""
AUTOSAR ARXML Merger Package

Ein Python-Modul zum Mergen von AUTOSAR ARXML-Dateien basierend auf dem Splitable Elements Ansatz.
"""

from .core.merger import ArxmlMerger
from .core.models import MergeResult, MergeConfig, ConflictResolutionStrategy
from .core.exceptions import ArxmlMergerException, SchemaValidationError, MergeConflictError

__version__ = "0.1.0"
__author__ = "Lukas"
__email__ = ""

__all__ = [
    "ArxmlMerger",
    "MergeResult", 
    "MergeConfig",
    "ConflictResolutionStrategy",
    "ArxmlMergerException",
    "SchemaValidationError",
    "MergeConflictError",
]
