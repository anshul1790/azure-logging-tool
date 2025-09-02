import os
import logging
from typing import List, Dict, Any, Optional
from datetime import timedelta

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryStatus
from azure.core.exceptions import HttpResponseError

from ..models.config import EnvironmentConfig
from ..models.entities import FunctionAppLogEntry
from ..models.exceptions import QueryError, AuthenticationError
from ..core.azure_client import AzureClientManager
from ..core.query_builder import KQLQueryBuilder
from ..core.response_parser import ResponseParser


class LogsService:
    """Service for retrieving and processing Azure Function App logs."""
    
    def __init__(self, config: EnvironmentConfig, credential: DefaultAzureCredential, logger: Optional[logging.Logger] = None):
        """
        Initialize LogsService with shared config and credentials.

        Args:
            config: Environment configuration
            credential: Azure credential instance
            logger: Optional logger instance
        """
        self.config = config
        self.credential = credential
        self.logger = logger or self._setup_logging()

        # Use centralized core components
        self.azure_client = AzureClientManager(config=config, credential=credential)
        self.query_builder = KQLQueryBuilder()
        self.response_parser = ResponseParser()

        self.logger.info(f"Initialized LogsService for Application Insights: {config.app_insights_name}")

    @staticmethod
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
            logger.setLevel(getattr(logging, log_level, logging.INFO))
        return logger

    def get_logs(
        self,
        application_name: str,
        hours_back: int = 1,
        log_level: Optional[str] = "Information",
        function_name: Optional[str] = None,
        limit: int = 100
    ) -> List[FunctionAppLogEntry]:
        """
        Retrieve logs for Azure Application Insights instance.
        
        Args:
            application_name: Name of the Azure Application
            hours_back: Number of hours to look back
            log_level: Filter by log level (Error, Warning, Information, Verbose)
            function_name: Filter by specific function name
            limit: Maximum number of logs to retrieve

        Returns:
            List of FunctionAppLogEntry objects
        """
        try:
            self.logger.info(f"Retrieving logs for {application_name} (last {hours_back} hours)")
            
            # Build KQL query using centralized query builder
            query = self.query_builder.build_logs_query(
                application_name=application_name,
                hours_back=hours_back,
                log_level=log_level,
                function_name=function_name,
                limit=limit
            )
            
            self.logger.debug(f"Executing KQL query: \n{query}")

            # Calculate timespan for the query
            timespan = timedelta(hours=hours_back)
            
            # Execute query using centralized Azure client
            response = self.azure_client.logs_client.query_resource(
                resource_id=self.azure_client.get_app_insights_resource_id(),
                query=query,
                timespan=timespan
            )
            
            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                # Parse response using centralized parser
                logs = self.response_parser.parse_log_response(response.tables[0].rows)
                self.logger.info(f"Retrieved {len(logs)} log entries")
                return logs
            else:
                self.logger.warning("No logs found or query failed")
                return []
                
        except HttpResponseError as e:
            self.logger.error(f"Failed to query logs: {e}")
            raise QueryError(f"Failed to retrieve logs: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving logs: {e}")
            raise QueryError(f"Unexpected error retrieving logs: {e}")
    
    def get_error_logs(
        self,
        application_name: str,
        hours_back: int = 24,
        limit: int = 50
    ) -> List[FunctionAppLogEntry]:
        """
        Get only error-level logs for a Application

        Args:
            application_name: Name of the Application
            hours_back: Number of hours to look back
            limit: Maximum number of logs to retrieve

        Returns:
            List of error-level FunctionAppLogEntry objects
        """
        return self.get_logs(
            application_name=application_name,
            hours_back=hours_back,
            log_level="Error",
            limit=limit
        )
    
    def search_logs(
        self,
        application_name: str,
        search_term: str,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[FunctionAppLogEntry]:
        """
        Search logs containing specific text.
        
        Args:
            application_name: Name of the App
            search_term: Text to search for in log messages
            hours_back: Number of hours to look back
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of FunctionAppLogEntry objects containing the search term
        """
        try:
            self.logger.info(f"Searching logs for '{search_term}' in {application_name}")
            
            # Build custom search query
            query = f"""
            traces
            | where timestamp > ago({hours_back}h)
            | where cloud_RoleName contains '{application_name}'
            | where message contains '{search_term}'
            | limit {limit}
            | project timestamp, severityLevel, message, operation_Name, operation_Id, customDimensions
            | order by timestamp desc
            """
            
            timespan = timedelta(hours=hours_back)

            response = self.azure_client.logs_client.query_resource(
                resource_id=self.azure_client.get_app_insights_resource_id(),
                query=query,
                timespan=timespan
            )
            
            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                logs = self.response_parser.parse_log_response(response.tables[0].rows)
                self.logger.info(f"Found {len(logs)} logs containing '{search_term}'")
                return logs
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to search logs: {e}")
            raise QueryError(f"Failed to search logs: {e}")

    def get_function_logs(
        self,
        application_name: str,
        function_name: str,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[FunctionAppLogEntry]:
        """
        Get logs for a specific function within a Function App.

        Args:
            application_name: Name of the App
            function_name: Name of the specific function
            hours_back: Number of hours to look back
            limit: Maximum number of logs to retrieve

        Returns:
            List of FunctionAppLogEntry objects for the specific function
        """
        return self.get_logs(
            application_name=application_name,
            function_name=function_name,
            hours_back=hours_back,
            limit=limit
        )
