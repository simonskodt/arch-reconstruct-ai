"""Pytest configuration and fixtures."""
import os

def pytest_configure():  # noqa: ARG001
    """Configure pytest with required environment variables."""
    # Set default environment variables for testing
    if "AGENT_WORKSPACE_BASE_PATH" not in os.environ:
        os.environ["AGENT_WORKSPACE_BASE_PATH"] = "/tmp/test_workspace"
