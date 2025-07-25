import logging
from pathlib import Path
import tempfile
import os
import pytest
from logger import init_global_logger

def test_init_global_logger_file_only(tmp_path):
  log_file = tmp_path / "test.log"
  init_global_logger(log_file, enable_console=False, enable_file=True, level=logging.INFO)
  logger = logging.getLogger()
  # Should only have one handler (FileHandler)
  handlers = logger.handlers
  assert len(handlers) == 1
  assert isinstance(handlers[0], logging.FileHandler)
  # Log something and check file content
  logger.info("Test log entry")
  with open(log_file, "r") as f:
    content = f.read()
  assert "Test log entry" in content

def test_init_global_logger_console_only(monkeypatch):
  log_file = Path("dummy.log")
  init_global_logger(log_file, enable_console=True, enable_file=False, level=logging.WARNING)
  logger = logging.getLogger()
  handlers = logger.handlers
  assert len(handlers) == 1
  assert isinstance(handlers[0], logging.StreamHandler)
  # Check log level
  assert logger.level == logging.WARNING

def test_init_global_logger_both_handlers(tmp_path):
  log_file = tmp_path / "test_both.log"
  init_global_logger(log_file, enable_console=True, enable_file=True, level=logging.ERROR)
  logger = logging.getLogger()
  handler_types = [type(h) for h in logger.handlers]
  assert logging.StreamHandler in handler_types
  assert logging.FileHandler in handler_types
  assert logger.level == logging.ERROR

def test_init_global_logger_clears_handlers(tmp_path):
  log_file = tmp_path / "test_clear.log"
  logger = logging.getLogger()
  # Add a dummy handler
  dummy_handler = logging.StreamHandler()
  logger.addHandler(dummy_handler)
  assert dummy_handler in logger.handlers
  # Now init_global_logger should clear it
  init_global_logger(log_file)
  assert dummy_handler not in logger.handlers

def test_init_global_logger_sets_other_loggers(tmp_path):
  log_file = tmp_path / "test_other.log"
  init_global_logger(log_file, level=logging.CRITICAL)
  assert logging.getLogger("uvicorn").level == logging.CRITICAL
  assert logging.getLogger("uvicorn.error").level == logging.CRITICAL
  assert logging.getLogger("uvicorn.access").level == logging.CRITICAL
  assert logging.getLogger("fastapi").level == logging.CRITICAL