class AzureFunctionSDKError(Exception):
    """Base exception for Azure Function SDK."""
    pass


class ConfigurationError(AzureFunctionSDKError):
    """Configuration related errors."""
    pass


class AuthenticationError(AzureFunctionSDKError):
    """Authentication related errors."""
    pass


class QueryError(AzureFunctionSDKError):
    """Query execution errors."""
    pass