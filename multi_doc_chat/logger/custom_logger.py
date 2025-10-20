import os 
import logging 
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir = "logs"):
        self.log_dir = os.path.join(os.getcwd(), log_dir) 
        os.makedirs(self.log_dir, exist_ok=True) 
        
        log_file = datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + ".log"
        self.log_file_path = os.path.join(self.log_dir, log_file) 

    def get_logger(self, name = __file__):
        logger_name = os.path.basename(name) 

        # Configure logging + file 
        file_handler = logging.FileHandler(self.log_file_path) 
        file_handler.setLevel(logging.INFO) 
        file_handler.setFormatter(logging.Formatter("%(message)s")) # Raw JSON Lines 
        
        console_handler = logging.StreamHandler() 
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level = logging.INFO, 
            format = "%(message)s",
            handlers=(console_handler, file_handler)    
        )

        # Configuring structuring for JSON structured log 
        structlog.configure(
            processors = [
            structlog.processors.TimeStamper(fmt = "iso", utc = True, key = "timestamp"), 
            structlog.processors.add_log_level,
            structlog.processors.EventRenamer(to = 'event'), 
            structlog.processors.JSONRenderer()
            ], 
            logger_factory=structlog.stdlib.LoggerFactory(), 
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)

if __name__ == "__main__":
    logger = CustomLogger().get_logger(__file__)

    logger.info("Logger initialized successfully", app="CustomLoggerTest")
    logger.warning("This is a warning message", context="testing")
    logger.error("Something went wrong", error_code=500)