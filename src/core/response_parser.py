import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from ..models.entities import FunctionAppLogEntry, FunctionAppMetrics, ErrorAnalysis


class ResponseParser:
    """Parses Azure Monitor query responses into structured data."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_log_response(self, rows: List[List[Any]]) -> List[FunctionAppLogEntry]:
        """Parse Application Insights traces response into FunctionAppLogEntry objects."""
        logs = []
        
        # Severity level mapping for Application Insights
        severity_map = {
            0: "Verbose",
            1: "Information", 
            2: "Warning",
            3: "Error"
        }
        
        for row in rows:
            try:
                custom_props = None
                if len(row) > 5 and row[5]:
                    try:
                        custom_props = json.loads(row[5]) if isinstance(row[5], str) else row[5]
                    except (json.JSONDecodeError, TypeError):
                        custom_props = {"raw": str(row[5])}
                
                log_entry = FunctionAppLogEntry(
                    timestamp=row[0] if row[0] else datetime.now(),
                    level=severity_map.get(int(row[1]), "Unknown") if row[1] is not None else "Unknown",
                    message=row[2] or "",
                    function_name=row[3],  # operation_Name
                    invocation_id=row[4],  # operation_Id
                    exception_type=None,   # Not available in traces
                    exception_message=None,
                    custom_properties=custom_props
                )
                logs.append(log_entry)
            except (IndexError, TypeError, ValueError) as e:
                self.logger.warning(f"Failed to parse log row: {e}")
                continue
        
        return logs

    def parse_metrics_response(self, rows: List[List[Any]]) -> List[FunctionAppMetrics]:
        """Parse Application Insights requests metrics response."""
        metrics = []
        for row in rows:
            try:
                metric = FunctionAppMetrics(
                    timestamp=row[0] if row[0] else datetime.now(),
                    total_invocations=int(row[1] or 0),
                    successful_invocations=int(row[2] or 0),
                    failed_invocations=int(row[3] or 0),
                    avg_duration_ms=float(row[4] or 0),
                    unique_functions=int(row[5] or 0)
                )
                metrics.append(metric)
            except (IndexError, TypeError, ValueError) as e:
                self.logger.warning(f"Failed to parse metrics row: {e}")
                continue
        
        return metrics
    
    def parse_error_analysis_response(self, rows: List[List[Any]], function_app_name: str, hours_back: int) -> ErrorAnalysis:
        """Parse error analysis query response."""
        errors = []
        total_errors = 0
        
        for row in rows:
            try:
                error_info = {
                    "function_name": row[0] or "Unknown",
                    "exception_type": row[1] or "Unknown", 
                    "exception_message": row[2] or "Unknown",
                    "count": int(row[3] or 0)
                }
                errors.append(error_info)
                total_errors += error_info["count"]
            except (IndexError, TypeError, ValueError) as e:
                self.logger.warning(f"Failed to parse error row: {e}")
                continue
        
        return ErrorAnalysis(
            errors=errors,
            total_errors=total_errors,
            unique_error_types=len(errors),
            time_range_hours=hours_back,
            function_app_name=function_app_name
        )
    
    def parse_function_performance_response(self, rows: List[List[Any]]) -> List[Dict[str, Any]]:
        """Parse function performance analysis response."""
        performance_data = []
        
        for row in rows:
            try:
                perf_info = {
                    "function_name": row[0] or "Unknown",
                    "invocation_count": int(row[1] or 0),
                    "avg_duration_ms": float(row[2] or 0),
                    "min_duration_ms": float(row[3] or 0),
                    "max_duration_ms": float(row[4] or 0),
                    "p95_duration_ms": float(row[5] or 0),
                    "success_rate": float(row[6] or 0)
                }
                performance_data.append(perf_info)
            except (IndexError, TypeError, ValueError) as e:
                self.logger.warning(f"Failed to parse performance row: {e}")
                continue
        
        return performance_data
    
    def parse_timeline_response(self, rows: List[List[Any]]) -> List[Dict[str, Any]]:
        """Parse timeline analysis response."""
        timeline_data = []
        
        for row in rows:
            try:
                timeline_point = {
                    "timestamp": row[0] if row[0] else datetime.now(),
                    "requests": int(row[1] or 0),
                    "errors": int(row[2] or 0),
                    "traces": int(row[3] or 0)
                }
                timeline_data.append(timeline_point)
            except (IndexError, TypeError, ValueError) as e:
                self.logger.warning(f"Failed to parse timeline row: {e}")
                continue
        
        return timeline_data