"""
Schema module for AUTOSAR version support
"""

from .autosar_schema import (
    AutosarSchemaHandler,
    Autosar40SchemaHandler,
    Autosar41SchemaHandler,
    Autosar42SchemaHandler,
    Autosar431SchemaHandler,
    Autosar44SchemaHandler,
    Autosar2011SchemaHandler,
    Autosar2111SchemaHandler,
    Autosar2211SchemaHandler,
    Autosar2311SchemaHandler,
    Autosar2411SchemaHandler,
    SchemaDetector
)

__all__ = [
    "AutosarSchemaHandler",
    "Autosar40SchemaHandler",
    "Autosar41SchemaHandler", 
    "Autosar42SchemaHandler",
    "Autosar431SchemaHandler",
    "Autosar44SchemaHandler",
    "Autosar2011SchemaHandler",
    "Autosar2111SchemaHandler",
    "Autosar2211SchemaHandler",
    "Autosar2311SchemaHandler",
    "Autosar2411SchemaHandler",
    "SchemaDetector"
]
