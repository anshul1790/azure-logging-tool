import logging
import os
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup structured logging for the SDK.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Custom log format string
        log_file: Optional file path to write logs to
        
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use provided
    level = os.getenv('LOG_LEVEL', log_level).upper()
    
    # Default format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format=log_format,
        handlers=[]
    )
    
    logger = logging.getLogger('azure_function_logs_sdk')
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(log_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    logger.setLevel(getattr(logging, level, logging.INFO))
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'azure_function_logs_sdk.{name}')


def configure_azure_logging(enable_debug: bool = False):
    """
    Configure Azure SDK logging levels.
    
    Args:
        enable_debug: Enable debug logging for Azure SDKs
    """
    azure_loggers = [
        'azure.core.pipeline.policies.http_logging_policy',
        'azure.identity',
        'azure.mgmt.web',
        'azure.monitor.query'
    ]
    
    level = logging.DEBUG if enable_debug else logging.WARNING
    
    for logger_name in azure_loggers:
        azure_logger = logging.getLogger(logger_name)
        azure_logger.setLevel(level)