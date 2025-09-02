import os
import logging
from typing import List, Optional
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from ..models.config import EnvironmentConfig
from ..models.exceptions import QueryError
from ..core.azure_client import AzureClientManager


class FunctionAppService:
    """Service for managing Function App discovery and metadata."""

    def __init__(self, config: EnvironmentConfig, credential: DefaultAzureCredential, logger: Optional[logging.Logger] = None):
        """
        Initialize FunctionAppService with shared config and credentials.

        Args:
            config: Environment configuration
            credential: Azure credential instance
            logger: Optional logger instance
        """
        self.config = config
        self.credential = credential
        self.logger = logger or self._setup_logging()

        # Use centralized Azure client manager
        self.azure_client = AzureClientManager(config=config, credential=credential)

        self.logger.info(f"Initialized FunctionAppService for resource group: {config.resource_group}")

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

    def list_function_apps(self) -> List[str]:
        """
        List all Function Apps in the configured resource group.
        
        Returns:
            List of Function App names
        """
        try:
            self.logger.debug(f"Listing Function Apps in resource group: {self.config.resource_group}")

            function_apps = []
            apps = self.azure_client.web_client.web_apps.list_by_resource_group(self.config.resource_group)

            for app in apps:
                if app.kind and 'functionapp' in app.kind.lower():
                    function_apps.append(app.name)
                    self.logger.debug(f"Found Function App: {app.name}")
            
            self.logger.info(f"Found {len(function_apps)} Function Apps")
            return function_apps
            
        except ResourceNotFoundError:
            self.logger.error(f"Resource group not found: {self.config.resource_group}")
            raise QueryError(f"Resource group not found: {self.config.resource_group}")
        except HttpResponseError as e:
            self.logger.error(f"Failed to list Function Apps: {e}")
            raise QueryError(f"Failed to list Function Apps: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error listing Function Apps: {e}")
            raise QueryError(f"Unexpected error listing Function Apps: {e}")
    
    def list_functions(self, function_app_name: str) -> List[str]:
        """
        List all functions in a specific Function App.
        
        Args:
            function_app_name: Name of the Function App
            
        Returns:
            List of function names
        """
        try:
            self.logger.info(f"Listing functions in Function App: {function_app_name}")
            
            functions = []
            function_list = self.azure_client.web_client.web_apps.list_functions(
                resource_group_name=self.config.resource_group,
                name=function_app_name
            )
            
            for func in function_list:
                functions.append(func.name)
                self.logger.info(f"Found function: {func.name}")
            
            self.logger.info(f"Found {len(functions)} functions in {function_app_name}")
            return functions
            
        except ResourceNotFoundError:
            self.logger.error(f"Function App not found: {function_app_name}")
            raise QueryError(f"Function App not found: {function_app_name}")
        except HttpResponseError as e:
            self.logger.error(f"Failed to list functions: {e}")
            raise QueryError(f"Failed to list functions: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error listing functions: {e}")
            raise QueryError(f"Unexpected error listing functions: {e}")
    
    def get_function_app_info(self, function_app_name: str) -> dict:
        """
        Get detailed information about a Function App.
        
        Args:
            function_app_name: Name of the Function App
            
        Returns:
            Dictionary with Function App details
        """
        try:
            self.logger.info(f"Getting info for Function App: {function_app_name}")
            
            app = self.azure_client.web_client.web_apps.get(
                resource_group_name=self.config.resource_group,
                name=function_app_name
            )
            
            app_info = {
                "name": app.name,
                "resource_group": app.resource_group,
                "location": app.location,
                "kind": app.kind,
                "state": app.state,
                "host_name": app.default_host_name,
                "runtime_version": getattr(app.site_config, 'python_version', None) or \
                                getattr(app.site_config, 'node_version', None) or \
                                getattr(app.site_config, 'net_framework_version', None),
                "app_settings": {}
            }
            
            # Get app settings if available
            try:
                settings = self.azure_client.web_client.web_apps.list_application_settings(
                    resource_group_name=self.config.resource_group,
                    name=function_app_name
                )
                app_info["app_settings"] = dict(settings.properties) if settings.properties else {}
            except Exception as e:
                self.logger.warning(f"Could not retrieve app settings: {e}")
                app_info["app_settings"] = {}
            
            return app_info
            
        except ResourceNotFoundError:
            self.logger.error(f"Function App not found: {function_app_name}")
            raise QueryError(f"Function App not found: {function_app_name}")
        except Exception as e:
            self.logger.error(f"Failed to get Function App info: {e}")
            raise QueryError(f"Failed to get Function App info: {e}")
    
    def validate_function_app_exists(self, function_app_name: str) -> bool:
        """
        Check if a Function App exists in the resource group.
        
        Args:
            function_app_name: Name of the Function App
            
        Returns:
            True if Function App exists, False otherwise
        """
        try:
            function_apps = self.list_function_apps()
            return function_app_name in function_apps
        except Exception as e:
            self.logger.error(f"Failed to validate Function App existence: {e}")
            return False
