import json
import csv
import os
from typing import List, Dict, Any, Union
from datetime import datetime

from ..models.entities import FunctionAppLogEntry, FunctionAppMetrics, ErrorAnalysis


def export_to_json(
    data: Union[List[FunctionAppLogEntry], List[FunctionAppMetrics], ErrorAnalysis, List[Dict[str, Any]]],
    file_path: str,
    indent: int = 2
) -> str:
    """
    Export data to JSON file.
    
    Args:
        data: Data to export
        file_path: Output file path
        indent: JSON indentation
        
    Returns:
        Path to created file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Convert data to serializable format
    serializable_data = _convert_to_serializable(data)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=indent, ensure_ascii=False, default=str)
    
    return file_path


def export_to_csv(
    data: Union[List[FunctionAppLogEntry], List[FunctionAppMetrics], List[Dict[str, Any]]],
    file_path: str
) -> str:
    """
    Export data to CSV file.
    
    Args:
        data: Data to export (must be list)
        file_path: Output file path
        
    Returns:
        Path to created file
    """
    if not isinstance(data, list) or not data:
        raise ValueError("Data must be a non-empty list for CSV export")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Convert data to dictionaries
    dict_data = _convert_to_dict_list(data)
    
    # Write CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        if dict_data:
            writer = csv.DictWriter(f, fieldnames=dict_data[0].keys())
            writer.writeheader()
            writer.writerows(dict_data)
    
    return file_path


def export_logs_to_csv(logs: List[FunctionAppLogEntry], file_path: str) -> str:
    """
    Export logs to CSV with specific formatting.
    
    Args:
        logs: List of log entries
        file_path: Output file path
        
    Returns:
        Path to created file
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Timestamp', 'Level', 'Function Name', 'Invocation ID', 
            'Message', 'Exception Type', 'Exception Message'
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.timestamp.isoformat(),
                log.level,
                log.function_name or '',
                log.invocation_id or '',
                log.message,
                log.exception_type or '',
                log.exception_message or ''
            ])
    
    return file_path


def export_metrics_to_csv(metrics: List[FunctionAppMetrics], file_path: str) -> str:
    """
    Export metrics to CSV with specific formatting.
    
    Args:
        metrics: List of metrics
        file_path: Output file path
        
    Returns:
        Path to created file
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Timestamp', 'Total Invocations', 'Successful Invocations',
            'Failed Invocations', 'Avg Duration (ms)', 'Unique Functions'
        ])
        
        # Write data
        for metric in metrics:
            writer.writerow([
                metric.timestamp.isoformat(),
                metric.total_invocations,
                metric.successful_invocations,
                metric.failed_invocations,
                metric.avg_duration_ms,
                metric.unique_functions
            ])
    
    return file_path


def _convert_to_serializable(data: Any) -> Any:
    """Convert data to JSON serializable format."""
    if isinstance(data, list):
        return [_convert_to_serializable(item) for item in data]
    elif hasattr(data, '__dict__'):
        # Convert dataclass or object to dict
        result = {}
        for key, value in data.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = _convert_to_serializable(value)
        return result
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data


def _convert_to_dict_list(data: List[Any]) -> List[Dict[str, Any]]:
    """Convert list of objects to list of dictionaries."""
    result = []
    
    for item in data:
        if isinstance(item, dict):
            # Convert datetime objects in dict
            item_dict = {}
            for key, value in item.items():
                if isinstance(value, datetime):
                    item_dict[key] = value.isoformat()
                else:
                    item_dict[key] = value
            result.append(item_dict)
        elif hasattr(item, '__dict__'):
            # Convert dataclass or object to dict
            item_dict = {}
            for key, value in item.__dict__.items():
                if isinstance(value, datetime):
                    item_dict[key] = value.isoformat()
                else:
                    item_dict[key] = value
            result.append(item_dict)
        else:
            result.append({'value': str(item)})
    
    return result


def create_export_filename(
    base_name: str,
    function_app_name: str,
    data_type: str,
    extension: str = 'json',
    include_timestamp: bool = True
) -> str:
    """
    Create a standardized export filename.
    
    Args:
        base_name: Base filename
        function_app_name: Function App name
        data_type: Type of data (logs, metrics, errors)
        extension: File extension
        include_timestamp: Whether to include timestamp
        
    Returns:
        Formatted filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
    
    parts = [base_name, function_app_name, data_type]
    if timestamp:
        parts.append(timestamp)
    
    filename = "_".join(part for part in parts if part)
    return f"{filename}.{extension}"