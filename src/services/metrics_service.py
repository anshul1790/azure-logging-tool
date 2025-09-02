import os
import logging
from typing import List, Dict, Any, Optional
from datetime import timedelta

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryStatus
from azure.core.exceptions import HttpResponseError

from ..models.config import EnvironmentConfig
from ..models.entities import FunctionAppMetrics, ErrorAnalysis
from ..models.exceptions import QueryError, AuthenticationError
from ..core.azure_client import AzureClientManager
from ..core.query_builder import KQLQueryBuilder
from ..core.response_parser import ResponseParser


class MetricsService:
    """Service for retrieving and processing Azure Function App metrics."""

    def __init__(self, config: EnvironmentConfig, credential: DefaultAzureCredential, logger: Optional[logging.Logger] = None):
        """
        Initialize MetricsService with shared config and credentials.

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

        self.logger.info(f"Initialized MetricsService for Application Insights: {config.app_insights_name}")

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

    def get_metrics(
        self,
        function_app_name: str,
        hours_back: int = 24,
        granularity_hours: int = 1
    ) -> List[FunctionAppMetrics]:
        """
        Retrieve performance metrics for a Function App.

        Args:
            function_app_name: Name of the Function App
            hours_back: Number of hours to look back
            granularity_hours: Time granularity in hours for metrics aggregation

        Returns:
            List of FunctionAppMetrics objects
        """
        try:
            self.logger.info(f"Retrieving metrics for {function_app_name} (last {hours_back} hours)")

            # Build KQL query using centralized query builder
            query = self.query_builder.build_metrics_query(
                function_app_name=function_app_name,
                hours_back=hours_back,
                granularity_hours=granularity_hours
            )

            self.logger.debug(f"Executing metrics query: {query}")

            timespan = timedelta(hours=hours_back)

            # Execute query using centralized Azure client
            response = self.azure_client.logs_client.query_resource(
                resource_id=self.azure_client.get_app_insights_resource_id(),
                query=query,
                timespan=timespan
            )

            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                # Parse response using centralized parser
                metrics = self.response_parser.parse_metrics_response(response.tables[0].rows)
                self.logger.info(f"Retrieved {len(metrics)} metric entries")
                return metrics
            else:
                self.logger.warning("No metrics found or query failed")
                return []

        except HttpResponseError as e:
            self.logger.error(f"Failed to query metrics: {e}")
            raise QueryError(f"Failed to retrieve metrics: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving metrics: {e}")
            raise QueryError(f"Unexpected error retrieving metrics: {e}")

    def analyze_errors(
        self,
        function_app_name: str,
        hours_back: int = 24,
        limit: int = 20
    ) -> ErrorAnalysis:
        """
        Analyze errors and exceptions for a Function App.

        Args:
            function_app_name: Name of the Function App
            hours_back: Number of hours to look back
            limit: Maximum number of error types to analyze

        Returns:
            ErrorAnalysis object containing error analysis results
        """
        try:
            self.logger.info(f"Analyzing errors for {function_app_name} (last {hours_back} hours)")

            # Build KQL query using centralized query builder
            query = self.query_builder.build_error_analysis_query(
                function_app_name=function_app_name,
                hours_back=hours_back,
                limit=limit
            )

            timespan = timedelta(hours=hours_back)

            # Execute query using centralized Azure client
            response = self.azure_client.logs_client.query_resource(
                resource_id=self.azure_client.get_app_insights_resource_id(),
                query=query,
                timespan=timespan
            )

            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                # Parse response using centralized parser
                analysis = self.response_parser.parse_error_analysis_response(
                    response.tables[0].rows,
                    function_app_name,
                    hours_back
                )
                self.logger.info(f"Analyzed {len(analysis.errors)} error types")
                return analysis
            else:
                self.logger.warning("No error data found")
                return ErrorAnalysis(
                    errors=[],
                    total_errors=0,
                    unique_error_types=0,
                    time_range_hours=hours_back,
                    function_app_name=function_app_name
                )

        except HttpResponseError as e:
            self.logger.error(f"Failed to analyze errors: {e}")
            raise QueryError(f"Failed to analyze errors: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error analyzing errors: {e}")
            raise QueryError(f"Unexpected error analyzing errors: {e}")

    def get_function_performance(
        self,
        function_app_name: str,
        hours_back: int = 24,
        function_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get performance metrics grouped by individual functions.

        Args:
            function_app_name: Name of the Function App
            hours_back: Number of hours to look back
            function_name: Optional specific function name to filter

        Returns:
            List of dictionaries containing per-function performance data
        """
        try:
            self.logger.info(f"Retrieving function performance for {function_app_name}")

            # Build KQL query using centralized query builder
            query = self.query_builder.build_function_performance_query(
                function_app_name=function_app_name,
                hours_back=hours_back,
                function_name=function_name
            )

            timespan = timedelta(hours=hours_back)

            # Execute query using centralized Azure client
            response = self.azure_client.logs_client.query_resource(
                resource_id=self.azure_client.get_app_insights_resource_id(),
                query=query,
                timespan=timespan
            )

            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                # Parse response using centralized parser
                performance_data = self.response_parser.parse_function_performance_response(response.tables[0].rows)
                self.logger.info(f"Retrieved performance data for {len(performance_data)} functions")
                return performance_data
            else:
                return []

        except Exception as e:
            self.logger.error(f"Failed to get function performance: {e}")
            raise QueryError(f"Failed to get function performance: {e}")

    def get_timeline_analysis(
        self,
        function_app_name: str,
        hours_back: int = 24,
        granularity_minutes: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Get timeline analysis showing activity over time.

        Args:
            function_app_name: Name of the Function App
            hours_back: Number of hours to look back
            granularity_minutes: Time granularity in minutes

        Returns:
            List of dictionaries containing timeline data
        """
        try:
            self.logger.info(f"Retrieving timeline analysis for {function_app_name}")

            # Build KQL query using centralized query builder
            query = self.query_builder.build_timeline_query(
                function_app_name=function_app_name,
                hours_back=hours_back,
                granularity_minutes=granularity_minutes
            )

            timespan = timedelta(hours=hours_back)

            # Execute query using centralized Azure client
            response = self.azure_client.logs_client.query_resource(
                resource_id=self.azure_client.get_app_insights_resource_id(),
                query=query,
                timespan=timespan
            )

            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                # Parse response using centralized parser
                timeline_data = self.response_parser.parse_timeline_response(response.tables[0].rows)
                self.logger.info(f"Retrieved timeline data with {len(timeline_data)} data points")
                return timeline_data
            else:
                return []

        except Exception as e:
            self.logger.error(f"Failed to get timeline analysis: {e}")
            raise QueryError(f"Failed to get timeline analysis: {e}")
