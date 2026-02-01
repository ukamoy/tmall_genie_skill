# app/middleware/logger_state.py
import logging
import sys
from fastapi import Request

def create_logger(name="aligenie"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

async def add_logger_to_state(request: Request, call_next):
    # 初始化 logger 并挂到 request.state
    request.state.logger = create_logger()
    response = await call_next(request)
    return response
