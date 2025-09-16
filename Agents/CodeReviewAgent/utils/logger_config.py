"""
Logging configuration for the ReviewAgent.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class LoggerConfig:
    """Configuration manager for logging."""
    
    @staticmethod
    def setup_logging(
        level: str = "INFO",
        log_file: Optional[Path] = None,
        console_output: bool = True,
        format_string: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """Set up logging configuration."""
        
        # Convert string level to logging constant
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        # Default format
        if format_string is None:
            format_string = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(filename)s:%(lineno)d - %(message)s'
            )
        
        # Create formatter
        formatter = logging.Formatter(format_string)
        
        # Get root logger and clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(numeric_level)
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler to prevent huge log files
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        return root_logger
    
    @staticmethod
    def setup_from_config(config: Dict[str, Any]):
        """Set up logging from configuration dictionary."""
        log_config = config.get('logging', {})
        
        level = log_config.get('level', 'INFO')
        log_file_path = log_config.get('log_file')
        console_output = log_config.get('console_output', True)
        format_string = log_config.get('format')
        max_file_size = log_config.get('max_file_size_mb', 10) * 1024 * 1024
        backup_count = log_config.get('backup_count', 5)
        
        log_file = Path(log_file_path) if log_file_path else None
        
        return LoggerConfig.setup_logging(
            level=level,
            log_file=log_file,
            console_output=console_output,
            format_string=format_string,
            max_file_size=max_file_size,
            backup_count=backup_count
        )
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)
    
    @staticmethod
    def set_level_for_logger(logger_name: str, level: str):
        """Set level for a specific logger."""
        logger = logging.getLogger(logger_name)
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)
    
    @staticmethod
    def add_file_handler(
        logger_name: str,
        log_file: Path,
        level: str = "INFO",
        format_string: Optional[str] = None
    ):
        """Add a file handler to a specific logger."""
        logger = logging.getLogger(logger_name)
        
        if format_string is None:
            format_string = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(filename)s:%(lineno)d - %(message)s'
            )
        
        formatter = logging.Formatter(format_string)
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return file_handler
    
    @staticmethod
    def create_review_logger(output_dir: Path, review_id: str) -> logging.Logger:
        """Create a logger specifically for a review session."""
        logger_name = f"review_{review_id}"
        logger = logging.getLogger(logger_name)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Set up file handler for this review
        log_file = output_dir / f"review_{review_id}.log"
        LoggerConfig.add_file_handler(logger_name, log_file)
        
        # Also add console handler if root logger doesn't have one
        if not any(isinstance(h, logging.StreamHandler) for h in logging.getLogger().handlers):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        logger.setLevel(logging.INFO)
        return logger
