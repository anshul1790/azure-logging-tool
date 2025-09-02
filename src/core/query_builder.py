from typing import Optional


class KQLQueryBuilder:
    """Builds KQL queries for Azure Application Insights."""
    
    @staticmethod
    def build_logs_query(
        application_name: str,
        hours_back: int,
        log_level: Optional[str] = None,
        function_name: Optional[str] = None,
        limit: int = 100,
        exclude_noise: bool = True
    ) -> str:
        """Build KQL query for logs retrieval from Application Insights."""
        query_parts = [
            "traces",
            f"| where timestamp > ago({hours_back}h)",
            f"| where cloud_RoleName contains '{application_name}'"
        ]
    
        # Filter by severity level if specified
        if log_level:
            severity_map = {
                "Error": "3",
                "Warning": "2", 
                "Information": "1",
                "Verbose": "0"
            }
            severity = severity_map.get(log_level, log_level)
            query_parts.append(f"| where severityLevel == {severity}")
        
        # Filter by function name if specified
        if function_name:
            query_parts.append(f"| where operation_Name contains '{function_name}' or message contains '{function_name}'")
        
        # Exclude common noise
        if exclude_noise:
            query_parts.extend([
                '| where message != "WorkerStatusRequest completed"',
                '| where message !contains "Host lock lease acquired"',
                '| where message !contains "Host lock lease renewed"'
            ])
        
        query_parts.extend([
            f"| limit {limit}",
            "| project timestamp, severityLevel, message, operation_Name, operation_Id, customDimensions",
            "| order by timestamp desc"
        ])
        
        return "\n".join(query_parts)
    
    @staticmethod
    def build_metrics_query(
        function_app_name: str,
        hours_back: int,
        granularity_hours: int = 1
    ) -> str:
        """Build KQL query for metrics retrieval from Application Insights."""
        return f"""
        requests
        | where timestamp > ago({hours_back}h)
        | where cloud_RoleName contains '{function_app_name}'
        | summarize 
            TotalRequests = count(),
            SuccessfulRequests = countif(success == true),
            FailedRequests = countif(success == false),
            AvgDuration = avg(duration),
            UniqueOperations = dcount(operation_Name)
        by bin(timestamp, {granularity_hours}h)
        | order by timestamp desc
        """
    
    @staticmethod
    def build_error_analysis_query(
        function_app_name: str,
        hours_back: int,
        limit: int = 20
    ) -> str:
        """Build KQL query for error analysis from Application Insights."""
        return f"""
        union traces, exceptions
        | where timestamp > ago({hours_back}h)
        | where cloud_RoleName contains '{function_app_name}'
        | where severityLevel >= 3 or itemType == "exception"
        | summarize ErrorCount = count() by 
            operation_Name, 
            type = iff(itemType == "exception", type, "trace"),
            message = iff(itemType == "exception", outerMessage, message)
        | order by ErrorCount desc
        | limit {limit}
        """
    
    @staticmethod
    def build_function_performance_query(
        function_app_name: str,
        hours_back: int,
        function_name: Optional[str] = None
    ) -> str:
        """Build query for function performance analysis."""
        base_query = f"""
        requests
        | where timestamp > ago({hours_back}h)
        | where cloud_RoleName contains '{function_app_name}'
        """
        
        if function_name:
            base_query += f"\n| where operation_Name contains '{function_name}'"
        
        base_query += """
        | summarize 
            InvocationCount = count(),
            AvgDuration = avg(duration),
            MinDuration = min(duration),
            MaxDuration = max(duration),
            P95Duration = percentile(duration, 95),
            SuccessRate = round(100.0 * countif(success == true) / count(), 2)
        by operation_Name
        | order by InvocationCount desc
        """
        
        return base_query
    
    @staticmethod
    def build_timeline_query(
        function_app_name: str,
        hours_back: int,
        granularity_minutes: int = 15
    ) -> str:
        """Build query for timeline analysis."""
        return f"""
        union requests, traces, exceptions
        | where timestamp > ago({hours_back}h)
        | where cloud_RoleName contains '{function_app_name}'
        | summarize 
            Requests = countif(itemType == "request"),
            Errors = countif(severityLevel >= 3 or itemType == "exception"),
            Traces = countif(itemType == "trace")
        by bin(timestamp, {granularity_minutes}m)
        | order by timestamp desc
        """