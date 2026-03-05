import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(service_name: str)-> logging.Logger:

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # to prevent duplicate handlers

    if logger.handlers:
        return logger
    
    log_format = (
        "%(asctime)s %(levelname)s %(name)s "
        "service=%(service)s %(message)s"
        )
    
    # formatter = logging.Formatter(log_format)      normal format
    formatter = jsonlogger.JsonFormatter(log_format)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


    return logging.LoggerAdapter(logger, {"service": service_name})
    

