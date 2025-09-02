import os
from dotenv import load_dotenv
import logging
from typing import List, Optional, Union, Dict, Any

from azure.identity import DefaultAzureCredential

from src.models.config import Environment, Config
from src.models.entities import FunctionAppLogEntry, FunctionAppMetrics, ErrorAnalysis
from src.models.exceptions import AuthenticationError, ConfigurationError
from src.services.function_app_service import FunctionAppService
from src.services.logs_service import LogsService
from archives.metrics_service import MetricsService

load_dotenv()

class AzureObservabilitySDK:
    """
    Azure SDK for Function Apps management, discovery, logs analysis, and metrics monitoring.

    Features:
    - Environment-based configuration
    - Comprehensive error handling
    - Structured logging
    - Modular service architecture using core components
    - Centralized Azure client management
    """

    def __init__(self, environment: Union[Environment, str], credential: Optional[DefaultAzureCredential] = None):
        """
        Initialize the SDK.

        Args:
            environment: Target environment (optumdev/optumqa)
            credential: Azure credential (optional, will create DefaultAzureCredential if not provided)
        """
        # Setup logging first
        self.logger = self._setup_logging()

        # Parse and validate environment
        if isinstance(environment, str):
            try:
                environment = Environment(environment.lower())
            except ValueError:
                valid_envs = [e.value for e in Environment]
                raise ConfigurationError(f"Invalid environment: {environment}. Valid options: {valid_envs}")

        self.environment = environment

        # Load configuration from environment variables
        try:
            self.config = Config.get_environment_config(environment.value)
            self.logger.info(f"Loaded configuration for environment: {environment.value}")
        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            raise ConfigurationError(f"Configuration error: {e}")

        # Initialize Azure credentials (shared across all services)
        try:
            self.credential = credential or DefaultAzureCredential()
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Azure credentials: {e}")

        # Initialize services with shared config and credentials
        try:
            self.function_app_service = FunctionAppService(
                config=self.config,
                credential=self.credential,
                logger=self.logger
            )

            self.logs_service = LogsService(
                config=self.config,
                credential=self.credential,
                logger=self.logger
            )

            self.metrics_service = MetricsService(
                config=self.config,
                credential=self.credential,
                logger=self.logger
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize services: {e}")

        self.logger.info(f"Initialized AzureMainSDK for environment: {environment.value}")

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Get log level from environment or use INFO
            log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
            logger.setLevel(getattr(logging, log_level, logging.INFO))
        return logger

    # Function App methods (delegate to service)
    def list_function_apps(self) -> List[str]:
        """List all Function Apps in the configured resource group."""
        return self.function_app_service.list_function_apps()

    def list_functions(self, function_app_name: str) -> List[str]:
        """List all functions in a specific Function App."""
        return self.function_app_service.list_functions(function_app_name)

    def get_function_app_info(self, function_app_name: str) -> dict:
        """Get detailed information about a Function App."""
        return self.function_app_service.get_function_app_info(function_app_name)

    def validate_function_app_exists(self, function_app_name: str) -> bool:
        """Check if a Function App exists in the resource group."""
        return self.function_app_service.validate_function_app_exists(function_app_name)

    # Logs methods (delegate to logs service)
    def get_logs(
        self,
        application_name: str,
        hours_back: int = 1,
        log_level: Optional[str] = "Information",
        function_name: Optional[str] = None,
        limit: int = 100
    ) -> List[FunctionAppLogEntry]:
        """Retrieve logs for a Function App."""
        return self.logs_service.get_logs(
            application_name=application_name,
            hours_back=hours_back,
            log_level=log_level,
            function_name=function_name,
            limit=limit
        )

    def get_error_logs(
        self,
        function_app_name: str,
        hours_back: int = 24,
        limit: int = 50
    ) -> List[FunctionAppLogEntry]:
        """Get only error-level logs for a Function App."""
        return self.logs_service.get_error_logs(
            application_name=function_app_name,
            hours_back=hours_back,
            limit=limit
        )

    def search_logs(
        self,
        function_app_name: str,
        search_term: str,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[FunctionAppLogEntry]:
        """Search logs containing specific text."""
        return self.logs_service.search_logs(
            application_name=function_app_name,
            search_term=search_term,
            hours_back=hours_back,
            limit=limit
        )

    def get_function_logs(
        self,
        function_app_name: str,
        function_name: str,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[FunctionAppLogEntry]:
        """Get logs for a specific function within a Function App."""
        return self.logs_service.get_function_logs(
            application_name=function_app_name,
            function_name=function_name,
            hours_back=hours_back,
            limit=limit
        )

    # Metrics methods (delegate to metrics service)
    def get_metrics(
        self,
        function_app_name: str,
        hours_back: int = 24,
        granularity_hours: int = 1
    ) -> List[FunctionAppMetrics]:
        """Retrieve performance metrics for a Function App."""
        return self.metrics_service.get_metrics(
            function_app_name=function_app_name,
            hours_back=hours_back,
            granularity_hours=granularity_hours
        )

    def analyze_errors(
        self,
        function_app_name: str,
        hours_back: int = 24,
        limit: int = 20
    ) -> ErrorAnalysis:
        """Analyze errors and exceptions for a Function App."""
        return self.metrics_service.analyze_errors(
            function_app_name=function_app_name,
            hours_back=hours_back,
            limit=limit
        )

    def get_function_performance(
        self,
        function_app_name: str,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Get performance metrics grouped by individual functions."""
        return self.metrics_service.get_function_performance(
            function_app_name=function_app_name,
            hours_back=hours_back
        )

# Demo functions for testing the three main functionalities
def show_function_app_info(sdk: AzureObservabilitySDK, function_app_name: str):
    print(f"=== 1. Show Function App Demo: {function_app_name} ===\n")
    try:
        app_info = sdk.get_function_app_info(function_app_name)
        print(f"📱 App Details:")
        print(f"   Name: {app_info['name']}")
        print(f"   Location: {app_info['location']}")
        print(f"   State: {app_info['state']}")
        print(f"   Runtime: {app_info.get('runtime_version', 'Unknown')}")
        print(f"   Host: {app_info.get('host_name', 'Unknown')}")
        print()
    except Exception as e:
        print(f"❌ Could not retrieve app info: {e}\n")

    # List all functions in the app
    print("⚙️ Functions in this app:")
    try:
        functions = sdk.list_functions(function_app_name)
        if functions:
            for i, func in enumerate(functions, 1):
                print(f"   {i}. {func}")
        else:
            print("   No functions found")
        print()
    except Exception as e:
        print(f"   Could not retrieve functions: {e}\n")

    return True

def show_logs_demo(sdk: AzureObservabilitySDK, function_app_name: str):
    """Demonstrate various logs functionality."""
    print(f"=== 2. Logs Demo: {function_app_name} ===\n")

    # Get all recent logs
    print("📋 Recent logs (last 3 hours):")
    try:
        logs = sdk.get_logs(function_app_name, hours_back=3, limit=10)
        if logs:
            for i, log in enumerate(logs[:5], 1):  # Show first 5 logs
                timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "Unknown"
                message_preview = log.message[:150] + "..." if len(log.message) > 150 else log.message
                print(f"   {i}. [{timestamp}] {log.level}: {message_preview}")
            if len(logs) > 5:
                print(f"   ... and {len(logs) - 5} more logs")
        else:
            print("   No logs found")
        print()
    except Exception as e:
        print(f"   Error retrieving logs: {e}\n")

    # Search for specific terms
    print("🔍 Searching for 'error' in logs:")
    try:
        search_results = sdk.search_logs(function_app_name, "error", hours_back=24, limit=5)
        if search_results:
            for i, log in enumerate(search_results[:3], 1):  # Show first 3
                timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "Unknown"
                message_preview = log.message[:100] + "..." if len(log.message) > 100 else log.message
                print(f"   {i}. [{timestamp}] {message_preview}")
        else:
            print("   No logs containing 'error' found")
        print()
    except Exception as e:
        print(f"   Error searching logs: {e}\n")

    # Get error-level logs specifically
    print("🚨 Error-level logs (last 24 hours):")
    try:
        error_logs = sdk.get_error_logs(function_app_name, hours_back=24, limit=5)
        if error_logs:
            for i, log in enumerate(error_logs, 1):
                timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "Unknown"
                message_preview = log.message[:100] + "..." if len(log.message) > 100 else log.message
                print(f"   {i}. [{timestamp}] ERROR: {message_preview}")
        else:
            print("   No error-level logs found")
        print()
    except Exception as e:
        print(f"   Error retrieving error logs: {e}\n")

def show_metrics_demo(sdk: AzureObservabilitySDK, function_app_name: str):
    """Demonstrate metrics functionality."""
    print(f"=== 3. Metrics Demo: {function_app_name} ===\n")

    # Get performance metrics
    print("📊 Performance metrics (last 24 hours):")
    try:
        metrics = sdk.get_metrics(function_app_name, hours_back=24, granularity_hours=1)
        if metrics:
            # Show latest metrics
            latest_metric = metrics[0]
            print(f"   📈 Latest metrics:")
            print(f"   Total Invocations: {latest_metric.total_invocations}")
            print(f"   Successful: {latest_metric.successful_invocations}")
            print(f"   Failed: {latest_metric.failed_invocations}")
            print(f"   Avg Duration: {latest_metric.avg_duration_ms:.2f}ms")
            print(f"   Unique Functions: {latest_metric.unique_functions}")

            # Show trend over last few hours
            if len(metrics) > 1:
                print(f"\n   📈 Trend (last {min(5, len(metrics))} hours):")
                for i, metric in enumerate(metrics[:5]):
                    timestamp = metric.timestamp.strftime("%H:%M") if metric.timestamp else "Unknown"
                    print(f"   [{timestamp}] Total: {metric.total_invocations}, Failed: {metric.failed_invocations}")
        else:
            print("   No metrics found")
        print()
    except Exception as e:
        print(f"   Error retrieving metrics: {e}\n")

    # Analyze errors
    print("🚨 Error analysis:")
    try:
        error_analysis = sdk.analyze_errors(function_app_name, hours_back=24, limit=5)
        print(f"   📊 Analysis for {error_analysis.function_app_name}")
        print(f"   🕒 Time range: {error_analysis.time_range_hours} hours")
        print(f"   🔢 Total errors: {error_analysis.total_errors}")
        print(f"   🆔 Unique error types: {error_analysis.unique_error_types}")

        if error_analysis.errors and error_analysis.total_errors > 0:
            print("   🔴 Top errors:")
            for i, error in enumerate(error_analysis.errors[:3], 1):  # Show top 3 errors
                print(f"   {i}. Function: {error['function_name']}")
                print(f"      Type: {error['exception_type']}")
                print(f"      Message: {error['exception_message'][:80]}...")
                print(f"      Count: {error['count']}")
        else:
            print("   ✅ No errors found in the specified time range")
        print()
    except Exception as e:
        print(f"   Error analyzing errors: {e}\n")

    # Function performance breakdown
    print("⚡ Function performance breakdown:")
    try:
        performance = sdk.get_function_performance(function_app_name, hours_back=24)
        if performance:
            print(f"   Found performance data for {len(performance)} functions:")
            for i, func_perf in enumerate(performance[:3], 1):  # Show top 3 functions
                print(f"   {i}. {func_perf['function_name']}")
                print(f"      Total Calls: {func_perf['total_calls']}")
                print(f"      Success Rate: {func_perf['success_rate']:.1f}%")
                print(f"      Avg Duration: {func_perf['avg_duration_ms']:.2f}ms")
                print(f"      Max Duration: {func_perf['max_duration_ms']:.2f}ms")
        else:
            print("   No performance data found")
        print()
    except Exception as e:
        print(f"   Error retrieving function performance: {e}\n")
