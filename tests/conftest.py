"""Pytest configuration ensuring local src takes precedence."""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app import create_app
from src.config import TestConfig


@pytest.fixture
def app():
    test_db = Path(TestConfig.DATABASE_PATH)
    if test_db.exists():
        test_db.unlink()
    application = create_app(TestConfig)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()
