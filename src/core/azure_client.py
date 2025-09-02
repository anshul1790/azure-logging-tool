import logging
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.monitor.query import LogsQueryClient
from azure.core.exceptions import ClientAuthenticationError

from ..models.config import EnvironmentConfig
from ..models.exceptions import AuthenticationError


class AzureClientManager:
    """Manages Azure client instances with lazy initialization."""
    
    def __init__(self, config: EnvironmentConfig, credential: Optional[DefaultAzureCredential] = None):
        self.config = config
        self.credential = credential or DefaultAzureCredential()
        self.logger = logging.getLogger(__name__)
        
        self._web_client = None
        self._logs_client = None
    
    @property
    def web_client(self) -> WebSiteManagementClient:
        """Lazy initialization of Web Management Client."""
        if self._web_client is None:
            try:
                self._web_client = WebSiteManagementClient(
                    credential=self.credential,
                    subscription_id=self.config.subscription_id
                )
                self.logger.info("Initialized WebSiteManagementClient")
            except ClientAuthenticationError as e:
                raise AuthenticationError(f"Failed to authenticate web client: {e}")
        return self._web_client
    
    @property
    def logs_client(self) -> LogsQueryClient:
        """Lazy initialization of Logs Query Client."""
        if self._logs_client is None:
            try:
                self._logs_client = LogsQueryClient(credential=self.credential)
                self.logger.info("Initialized LogsQueryClient")
            except ClientAuthenticationError as e:
                raise AuthenticationError(f"Failed to authenticate logs client: {e}")
        return self._logs_client
    
    def get_app_insights_resource_id(self) -> str:
        """Build Application Insights resource ID."""
        return f"/subscriptions/{self.config.subscription_id}/resourceGroups/{self.config.resource_group}/providers/Microsoft.Insights/components/{self.config.app_insights_name}"