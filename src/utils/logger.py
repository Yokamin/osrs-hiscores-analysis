# src/utils/logger.py
import logging
import sys
from datetime import datetime

class CustomTimeFormatter(logging.Formatter):
    """
    Custom formatter to format log timestamps.

    This formatter extends the standard logging.Formatter to provide
    custom timestamp formatting for log records.
    """

    def formatTime(self, record, datefmt=None):
        """
        Format the timestamp for a log record.

        Args:
            record (logging.LogRecord): The log record to format.
            datefmt (str, optional): The date format string (not used in this implementation).

        Returns:
            str: Formatted timestamp string in 'YYYY-MM-DD HH:MM:SS' format.
        """
        return datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

class UTF8StreamHandler(logging.StreamHandler):
    """
    Stream handler that handles Unicode encode errors.

    This handler extends the standard logging.StreamHandler to properly
    handle Unicode encode errors when emitting log records.
    """

    def emit(self, record):
        """
        Emit a log record.

        This method overrides the standard emit method to handle Unicode encode errors
        by replacing problematic characters.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        except UnicodeEncodeError:
            stream.write(record.message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
            stream.write(self.terminator)

def setup_logging(log_file='hiscores.log', file_level=logging.INFO, console_level=logging.INFO):
    """
    Set up and configure the loggers.
    
    This function sets up two loggers: one for file logging and one for console logging.
    The file logger provides detailed logs, while the console logger provides simplified logs.

    Args:
        log_file (str): Name of the log file. Defaults to 'hiscores.log'.
        file_level (int): Logging level for file logger. Defaults to logging.INFO.
        console_level (int): Logging level for console logger. Defaults to logging.INFO.
    
    Returns:
        tuple: A tuple containing (file_logger, console_logger).
            file_logger (logging.Logger): Logger for file output.
            console_logger (logging.Logger): Logger for console output.

    Raises:
        IOError: If unable to create the log file.
    """
    
    # Create a root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set to DEBUG to allow all levels

    # File handler (detailed)
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(file_level)
        file_formatter = CustomTimeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except IOError as e:
        print(f"Warning: Unable to create log file. {e}")
        return None, None  # Return None if unable to create log file

    # Console handler (simplified)
    console_handler = UTF8StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    console_handler.setFormatter(console_formatter)

    # Create loggers
    file_logger = logging.getLogger('hiscores_file_log')
    console_logger = logging.getLogger('hiscores_console_log')
    
    # Add console handler only to console_logger
    console_logger.addHandler(console_handler)
    # Set propagate to True for console_logger
    console_logger.propagate = True

    return file_logger, console_logger

def get_module_logger(module_name):
    """
    Get a logger for a specific module.
    
    This function returns a logger instance for a given module name.
    It's useful for creating module-specific loggers.

    Args:
        module_name (str): Name of the module.
    
    Returns:
        logging.Logger: Logger instance for the specified module.
    """
    return logging.getLogger(module_name)

logger, console_logger = setup_logging()

# Usage example:
if __name__ == "__main__":
    logger.debug("This is a debug message (file only)")
    logger.info("This is an info message (file only)")
    console_logger.info("This is an info message (console and file)")
    console_logger.warning("This is a warning message (console and file)")
    
    # Example of module-level logger
    module_logger = get_module_logger(__name__)
    module_logger.info("This is a module-level log message")