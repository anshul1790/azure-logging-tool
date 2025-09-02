from typing import List, Dict, Any
from datetime import datetime

from ..models.entities import FunctionAppLogEntry, FunctionAppMetrics, ErrorAnalysis


def format_logs_output(logs: List[FunctionAppLogEntry], max_message_length: int = 100) -> str:
    """
    Format logs for console output.
    
    Args:
        logs: List of log entries
        max_message_length: Maximum length of log message to display
        
    Returns:
        Formatted string representation of logs
    """
    if not logs:
        return "No logs found."
    
    output = []
    output.append(f"📋 Found {len(logs)} log entries:\n")
    
    for i, log in enumerate(logs, 1):
        timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        message = log.message[:max_message_length] + "..." if len(log.message) > max_message_length else log.message
        
        # Add emoji based on log level
        level_emoji = {
            "Error": "🔴",
            "Warning": "🟡", 
            "Information": "🔵",
            "Verbose": "⚪"
        }.get(log.level, "⚫")
        
        output.append(f"{i:3d}. {level_emoji} [{timestamp}] {log.level}")
        if log.function_name:
            output.append(f"     Function: {log.function_name}")
        output.append(f"     Message: {message}")
        if log.invocation_id:
            output.append(f"     ID: {log.invocation_id[:8]}...")
        output.append("")
    
    return "\n".join(output)


def format_metrics_output(metrics: List[FunctionAppMetrics]) -> str:
    """
    Format metrics for console output.
    
    Args:
        metrics: List of metrics entries
        
    Returns:
        Formatted string representation of metrics
    """
    if not metrics:
        return "No metrics found."
    
    output = []
    output.append(f"📊 Found {len(metrics)} metric entries:\n")
    
    # Calculate totals
    total_invocations = sum(m.total_invocations for m in metrics)
    total_successful = sum(m.successful_invocations for m in metrics)
    total_failed = sum(m.failed_invocations for m in metrics)
    avg_duration = sum(m.avg_duration_ms for m in metrics) / len(metrics) if metrics else 0
    
    output.append(f"📈 Summary:")
    output.append(f"   Total Invocations: {total_invocations:,}")
    output.append(f"   Successful: {total_successful:,} ({(total_successful/total_invocations*100):.1f}%)" if total_invocations > 0 else "   Successful: 0")
    output.append(f"   Failed: {total_failed:,} ({(total_failed/total_invocations*100):.1f}%)" if total_invocations > 0 else "   Failed: 0")
    output.append(f"   Avg Duration: {avg_duration:.2f}ms\n")
    
    output.append("⏱️  Timeline:")
    for i, metric in enumerate(metrics[:10]):  # Show first 10 entries
        timestamp = metric.timestamp.strftime("%Y-%m-%d %H:%M")
        success_rate = (metric.successful_invocations / metric.total_invocations * 100) if metric.total_invocations > 0 else 0
        
        output.append(f"   {timestamp}: {metric.total_invocations:3d} requests, {success_rate:5.1f}% success, {metric.avg_duration_ms:6.2f}ms avg")
    
    if len(metrics) > 10:
        output.append(f"   ... and {len(metrics) - 10} more entries")
    
    return "\n".join(output)


def format_error_analysis_output(analysis: ErrorAnalysis) -> str:
    """
    Format error analysis for console output.
    
    Args:
        analysis: Error analysis results
        
    Returns:
        Formatted string representation of error analysis
    """
    if analysis.total_errors == 0:
        return "🟢 No errors found in the specified time range."
    
    output = []
    output.append(f"🚨 Error Analysis for {analysis.function_app_name} (last {analysis.time_range_hours}h):\n")
    output.append(f"   Total Errors: {analysis.total_errors:,}")
    output.append(f"   Unique Error Types: {analysis.unique_error_types}\n")
    
    if analysis.errors:
        output.append("🔴 Top Errors:")
        for i, error in enumerate(analysis.errors[:10], 1):  # Show top 10
            percentage = (error["count"] / analysis.total_errors * 100)
            output.append(f"{i:2d}. Function: {error['function_name']}")
            output.append(f"    Type: {error['exception_type']}")
            output.append(f"    Count: {error['count']:,} ({percentage:.1f}%)")
            
            # Truncate long error messages
            message = error['exception_message']
            if len(message) > 80:
                message = message[:80] + "..."
            output.append(f"    Message: {message}\n")
        
        if len(analysis.errors) > 10:
            output.append(f"   ... and {len(analysis.errors) - 10} more error types")
    
    return "\n".join(output)


def format_function_performance_output(performance_data: List[Dict[str, Any]]) -> str:
    """
    Format function performance data for console output.
    
    Args:
        performance_data: List of function performance dictionaries
        
    Returns:
        Formatted string representation of performance data
    """
    if not performance_data:
        return "No performance data found."
    
    output = []
    output.append(f"⚡ Function Performance Analysis ({len(performance_data)} functions):\n")
    
    # Sort by invocation count
    sorted_data = sorted(performance_data, key=lambda x: x['invocation_count'], reverse=True)
    
    for i, perf in enumerate(sorted_data[:15], 1):  # Show top 15
        output.append(f"{i:2d}. {perf['function_name']}")
        output.append(f"    Invocations: {perf['invocation_count']:,}")
        output.append(f"    Success Rate: {perf['success_rate']:.1f}%")
        output.append(f"    Avg Duration: {perf['avg_duration_ms']:.2f}ms")
        output.append(f"    P95 Duration: {perf['p95_duration_ms']:.2f}ms")
        output.append(f"    Range: {perf['min_duration_ms']:.2f}ms - {perf['max_duration_ms']:.2f}ms\n")
    
    if len(sorted_data) > 15:
        output.append(f"   ... and {len(sorted_data) - 15} more functions")
    
    return "\n".join(output)


def format_timeline_output(timeline_data: List[Dict[str, Any]]) -> str:
    """
    Format timeline data for console output.
    
    Args:
        timeline_data: List of timeline data points
        
    Returns:
        Formatted string representation of timeline
    """
    if not timeline_data:
        return "No timeline data found."
    
    output = []
    output.append(f"📈 Timeline Analysis ({len(timeline_data)} data points):\n")
    
    for point in timeline_data[:20]:  # Show first 20 points
        timestamp = point['timestamp'].strftime("%Y-%m-%d %H:%M")
        total_activity = point['requests'] + point['traces']
        error_rate = (point['errors'] / total_activity * 100) if total_activity > 0 else 0
        
        # Visual indicator for error rate
        if error_rate > 10:
            indicator = "🔴"
        elif error_rate > 5:
            indicator = "🟡"
        else:
            indicator = "🟢"
        
        output.append(f"{indicator} {timestamp}: {point['requests']:3d} req, {point['errors']:3d} err ({error_rate:4.1f}%), {point['traces']:4d} traces")
    
    if len(timeline_data) > 20:
        output.append(f"\n... and {len(timeline_data) - 20} more data points")
    
    return "\n".join(output)


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."