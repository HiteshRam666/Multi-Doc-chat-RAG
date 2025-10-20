from .custom_logger import CustomLogger as _CustomLogger 
try:
    from .custom_logger import CustomLogger 
except Exception as e:
    CustomLogger = _CustomLogger 

# Expose a global structlog-style logger used across the codebase
GLOBAL_LOGGER = CustomLogger().get_logger(__name__)