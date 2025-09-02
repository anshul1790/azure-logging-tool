from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class FunctionAppLogEntry:
    """Represents a single Function App log entry."""
    timestamp: datetime
    level: str
    message: str
    function_name: Optional[str] = None
    invocation_id: Optional[str] = None
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    custom_properties: Optional[Dict[str, Any]] = None


@dataclass
class FunctionAppMetrics:
    """Represents Function App metrics."""
    timestamp: datetime
    total_invocations: int
    successful_invocations: int
    failed_invocations: int
    avg_duration_ms: float
    unique_functions: int


@dataclass
class ErrorAnalysis:
    """Represents error analysis results."""
    errors: list
    total_errors: int
    unique_error_types: int
    time_range_hours: int
    function_app_name: str