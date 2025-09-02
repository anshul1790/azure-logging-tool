import os
from dotenv import load_dotenv
from ..core.azure_observability_sdk import AzureObservabilitySDK
from ..models import Environment

from langchain.tools import tool

load_dotenv()

@tool
def get_application_logs(application_name: str, hours_back: int = 1, limit: int = 100, log_level: str = "Information",) -> str:
    """
    Retrieve and summarize logs for a specified function app within a given time frame.
    """
    environment = os.getenv("AZURE_ENVIRONMENT", "optumqa")

    # try:
    #     sdk = AzureObservabilitySDK(Environment(environment.lower()))
    #     logs = sdk.get_logs(
    #         application_name=application_name,
    #         hours_back=hours_back,
    #         limit=limit,
    #         log_level=log_level
    #     )
    #
    #     if not logs:
    #         return f"No logs found for {application_name} in the last {hours_back} hours."
    #
    #     log_summary = f"Found {len(logs)} logs for {application_name} (last {hours_back} hours):\n\n"
    #
    #     for i, log in enumerate(logs[:10], 1):  # Show first 10 logs
    #         timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "Unknown"
    #         message_preview = log.message[:200] + "..." if len(log.message) > 200 else log.message
    #         log_summary += f"{i}. [{timestamp}] {log.level}: {message_preview}\n"
    #
    #     if len(logs) > 10:
    #         log_summary += f"\n... and {len(logs) - 10} more logs."
    #
    #     return log_summary
    #
    # except Exception as e:
    #     return f"Error retrieving logs for {application_name}: {str(e)}"
    try:
        # Dummy log data
        dummy_logs = [
            {
                "timestamp": "2025-09-02 09:15:23",
                "level": "Information",
                "message": f"{application_name} started successfully."
            },
            {
                "timestamp": "2025-09-02 09:20:45",
                "level": "Warning",
                "message": f"High memory usage detected in {application_name}."
            },
            {
                "timestamp": "2025-09-02 09:30:12",
                "level": "Error",
                "message": f"{application_name} encountered a transient error but recovered."
            },
            {
                "timestamp": "2025-09-02 09:40:55",
                "level": "Information",
                "message": f"{application_name} processed 120 requests."
            },
        ]

        if not dummy_logs:
            return f"No logs found for {application_name} in the last {hours_back} hours."

        # Apply limit
        logs = dummy_logs[:limit]

        log_summary = f"Found {len(logs)} logs for {application_name} (last {hours_back} hours):\n\n"

        for i, log in enumerate(logs[:10], 1):  # Show first 10 logs
            message_preview = log["message"][:200] + "..." if len(log["message"]) > 200 else log["message"]
            log_summary += f"{i}. [{log['timestamp']}] {log['level']}: {message_preview}\n"

        if len(dummy_logs) > 10:
            log_summary += f"\n... and {len(dummy_logs) - 10} more logs."

        return log_summary

    except Exception as e:
        return f"Error retrieving logs for {application_name}: {str(e)}"
