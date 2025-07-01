"""
Exception classes for the ARXML Merger
"""

class ArxmlMergerException(Exception):
    """Base exception for ARXML Merger errors"""
    pass


class SchemaValidationError(ArxmlMergerException):
    """Error during schema validation"""
    def __init__(self, message: str, schema_version: str = None, file_path: str = None):
        super().__init__(message)
        self.schema_version = schema_version
        self.file_path = file_path


class MergeConflictError(ArxmlMergerException):
    """Error during merge conflicts"""
    def __init__(self, message: str, element_path: str = None, conflicting_values: list = None):
        super().__init__(message)
        self.element_path = element_path
        self.conflicting_values = conflicting_values or []


class InvalidArxmlFileError(ArxmlMergerException):
    """Error with invalid ARXML files"""
    def __init__(self, message: str, file_path: str = None):
        super().__init__(message)
        self.file_path = file_path


class SplitKeyError(ArxmlMergerException):
    """Fehler bei der Split-Key Verarbeitung"""
    def __init__(self, message: str, split_key: str = None, element_path: str = None):
        super().__init__(message)
        self.split_key = split_key
        self.element_path = element_path
