"""
__init__.py für core Modul
"""

from .models import (
    MergeConfig,
    MergeResult,
    MergeStatistics,
    MergeConflict,
    ArxmlFile,
    ConflictResolutionStrategy
)
from .exceptions import (
    ArxmlMergerException,
    SchemaValidationError,
    MergeConflictError,
    InvalidArxmlFileError,
    SplitKeyError
)
from .merger import ArxmlMerger

__all__ = [
    "MergeConfig",
    "MergeResult", 
    "MergeStatistics",
    "MergeConflict",
    "ArxmlFile",
    "ConflictResolutionStrategy",
    "ArxmlMergerException",
    "SchemaValidationError",
    "MergeConflictError",
    "InvalidArxmlFileError",
    "SplitKeyError",
    "ArxmlMerger"
]
