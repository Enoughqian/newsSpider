"""Configures the logging of the application"""
from loguru import logger
import sys


def log_init(name='crawler'):
    format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} {line} | {elapsed} | {message} | {extra}"
    #logger.add(sys.stdout, level="DEBUG",
    #           format=format)

    logger.add(f'logs/{name}' + '-{time:YYYYMMDD}.log', rotation="00:00", level="DEBUG", enqueue=True,
               format=format)

    logger.add(f'logs/{name}' + '-{time:YYYYMMDD}.log.json', rotation="00:00", level="INFO", enqueue=True,
               serialize=True,
               format=format)


def log_init_simple(name='crawler'):
    format_str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} {line} | {elapsed} | {message} | {extra}"

    logger.add(f'logs/{name}' + '-{time:YYYYMMDD}.log', rotation="00:00", level="DEBUG", enqueue=True,
               format=format_str)
