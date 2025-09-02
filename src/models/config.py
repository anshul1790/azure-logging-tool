import os
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Environment(Enum):
    """Supported environments."""
    OPTUMDEV = "optumdev"
    OPTUMQA = "optumqa"


@dataclass
class EnvironmentConfig:
    """Configuration for each environment."""
    subscription_id: str
    resource_group: str
    app_insights_name: str


class Config:
    """Configuration manager."""
    
    @staticmethod
    def get_environment_config(environment: str) -> EnvironmentConfig:
        """Get configuration for specified environment from environment variables."""
        env_upper = environment.upper()
        
        subscription_id = os.getenv(f'{env_upper}_SUBSCRIPTION_ID')
        resource_group = os.getenv(f'{env_upper}_RESOURCE_GROUP')
        app_insights_name = os.getenv(f'{env_upper}_APP_INSIGHTS_NAME')
        
        if not all([subscription_id, resource_group, app_insights_name]):
            missing = [k for k, v in {
                'subscription_id': subscription_id,
                'resource_group': resource_group, 
                'app_insights_name': app_insights_name
            }.items() if not v]
            raise ValueError(f"Missing required environment variables for {environment}: {missing}")
        
        return EnvironmentConfig(
            subscription_id=subscription_id,
            resource_group=resource_group,
            app_insights_name=app_insights_name
        )