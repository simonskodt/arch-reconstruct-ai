# Test Commands

This document provides common pytest commands for running tests in the project.

The test suite is organized into:
- `unit_tests/`: Unit tests for individual components and functions
- `integration_tests/`: Integration tests for component interactions

# Run all tests
uv run --group test pytest tests/

# Run a specific test file
uv run --group test pytest tests/unit_tests/my_test.py

# Run a specific test function in a file
uv run --group test pytest tests/unit_tests/my_test.py::my_test_function

# Run a specific test function within a class
uv run --group test pytest tests/integration_tests/my_test.py::my_test_class::my_test_function
