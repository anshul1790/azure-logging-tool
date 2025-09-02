from typing import Union
from ..models.config import Environment


def validate_environment(environment: Union[str, Environment]) -> Environment:
    """
    Validate and convert environment string to Environment enum.
    
    Args:
        environment: Environment string or enum
        
    Returns:
        Valid Environment enum
        
    Raises:
        ValueError: If environment is invalid
    """
    if isinstance(environment, str):
        try:
            return Environment(environment.lower())
        except ValueError:
            valid_envs = [e.value for e in Environment]
            raise ValueError(f"Invalid environment: {environment}. Valid options: {valid_envs}")
    
    if isinstance(environment, Environment):
        return environment
    
    raise ValueError(f"Environment must be string or Environment enum, got {type(environment)}")


def validate_time_range(hours_back: int, max_hours: int = 8760) -> int:  # 8760 = 1 year
    """
    Validate time range parameters.
    
    Args:
        hours_back: Number of hours to look back
        max_hours: Maximum allowed hours (default: 1 year)
        
    Returns:
        Validated hours_back value
        
    Raises:
        ValueError: If time range is invalid
    """
    if not isinstance(hours_back, int):
        raise ValueError(f"hours_back must be an integer, got {type(hours_back)}")
    
    if hours_back <= 0:
        raise ValueError("hours_back must be a positive integer")
    
    if hours_back > max_hours:
        raise ValueError(f"hours_back cannot exceed {max_hours} hours")
    
    return hours_back


def validate_limit(limit: int, max_limit: int = 10000) -> int:
    """
    Validate query limit parameters.
    
    Args:
        limit: Query result limit
        max_limit: Maximum allowed limit
        
    Returns:
        Validated limit value
        
    Raises:
        ValueError: If limit is invalid
    """
    if not isinstance(limit, int):
        raise ValueError(f"limit must be an integer, got {type(limit)}")
    
    if limit <= 0:
        raise ValueError("limit must be a positive integer")
    
    if limit > max_limit:
        raise ValueError(f"limit cannot exceed {max_limit}")
    
    return limit


def validate_function_app_name(name: str) -> str:
    """
    Validate Function App name format.
    
    Args:
        name: Function App name
        
    Returns:
        Validated name
        
    Raises:
        ValueError: If name format is invalid
    """
    if not isinstance(name, str):
        raise ValueError(f"Function App name must be a string, got {type(name)}")
    
    if not name.strip():
        raise ValueError("Function App name cannot be empty")
    
    # Basic Azure naming validation
    if len(name) > 60:
        raise ValueError("Function App name cannot exceed 60 characters")
    
    # Check for invalid characters (basic check)
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', ' ', '\t', '\n']
    if any(char in name for char in invalid_chars):
        raise ValueError(f"Function App name contains invalid characters: {invalid_chars}")
    
    return name.strip()


def validate_log_level(log_level: str) -> str:
    """
    Validate log level parameter.
    
    Args:
        log_level: Log level string
        
    Returns:
        Validated log level
        
    Raises:
        ValueError: If log level is invalid
    """
    valid_levels = ["Error", "Warning", "Information", "Verbose"]
    
    if not isinstance(log_level, str):
        raise ValueError(f"log_level must be a string, got {type(log_level)}")
    
    # Case-insensitive matching
    for valid_level in valid_levels:
        if log_level.lower() == valid_level.lower():
            return valid_level
    
    raise ValueError(f"Invalid log level: {log_level}. Valid options: {valid_levels}")


def validate_granularity(granularity: int, min_granularity: int = 1, max_granularity: int = 24) -> int:
    """
    Validate time granularity parameters.
    
    Args:
        granularity: Time granularity value
        min_granularity: Minimum allowed granularity
        max_granularity: Maximum allowed granularity
        
    Returns:
        Validated granularity value
        
    Raises:
        ValueError: If granularity is invalid
    """
    if not isinstance(granularity, int):
        raise ValueError(f"granularity must be an integer, got {type(granularity)}")
    
    if granularity < min_granularity:
        raise ValueError(f"granularity must be at least {min_granularity}")
    
    if granularity > max_granularity:
        raise ValueError(f"granularity cannot exceed {max_granularity}")
    
    return granularity