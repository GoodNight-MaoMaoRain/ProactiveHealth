import sys
import logging
from loguru import logger
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    title: str = "主动健康项目"
    version: str = "1.0"
    host: str = "192.168.10.59"
    port: int = 8005
    debug: bool = True

    database_url: str = "postgresql://wzy:123456@127.0.0.1/health"
    allowed_hosts: list[str] = ["*"]

    logging_level: int = logging.INFO
    log_retention_days: int = 10

    class Config:
        env_file = ".env"

    def configure_logging(self):
        logger.add(sys.stdout, level=self.logging_level)

