"""Helper methods for loading MCP config with environment variable substitution and sanitization."""

import re
from typing import Any, Dict, Optional, List

from experiments.utils import utils_configurations


class ConfigSanitizer:
    """Recursively sanitizes configuration objects
    by redacting secrets and tracking leak locations."""

    def __init__(self):
        """Initialize the sanitizer with secret detection patterns."""
        self.leaks: List[str] = []
        self._secret_key_tokens = (
            "api_key",
            "apikey",
            "key",
            "secret",
            "token",
            "password",
            "authorization"
        )
        self._bearer_regex = re.compile(r'^(?P<scheme>Bearer\s+)(?P<token>\S+)',
                                        re.IGNORECASE)

    def sanitize(self, obj: Any, path_tuple: tuple[str, ...] = ()) -> Any:
        """
        Sanitize a configuration object by redacting secrets.

        Args:
            obj: The configuration object to sanitize
            path_tuple: Current path in the object hierarchy

        Returns:
            The sanitized configuration object
        """
        return self._sanitize(obj, path_tuple)

    def _sanitize(self, obj: Any, path_tuple: tuple[str, ...]) -> Any:
        """Internal recursive sanitization method."""
        # Handle dictionaries
        if isinstance(obj, dict):
            return self._sanitize_dictionary(obj, path_tuple)

        # Handle lists
        if isinstance(obj, list):
            return self._sanitize_list(obj, path_tuple)

        # Handle plain strings that might be Authorization header values
        if isinstance(obj, str) and path_tuple and self._is_secret_key(path_tuple[-1], obj):
            return self._sanitize_string(obj, path_tuple)

        # Fallback: return as-is
        return obj

    def _sanitize_dictionary(self, obj: dict, path_tuple: tuple[str, ...]) -> dict:
        """Sanitize a dictionary by processing each key-value pair."""
        sanitized: Dict[str, Any] = {}
        for key, value in obj.items():
            current_path = path_tuple + (key,)

            # Keys that look like secrets -> redact (special-case Bearer tokens)
            if self._is_secret_key(key, value):
                if isinstance(value, str):
                    match = self._bearer_regex.match(value)
                    sanitized[key] = f"{match.group('scheme')}<REDACTED>" if match else "<REDACTED>"
                else:
                    sanitized[key] = "<REDACTED>"
                self._mark_leak(current_path)
                continue

            # Recurse for nested structures
            if isinstance(value, (dict, list)):
                sanitized[key] = self._sanitize(value, current_path)
                continue

            # Non-secret primitive
            sanitized[key] = value
        return sanitized

    def _sanitize_list(self, obj: list, path_tuple: tuple[str, ...]) -> list:
        """Sanitize a list by processing each element."""
        sanitized_list: List[Any] = []
        for i, item in enumerate(obj):
            item_path = path_tuple + (str(i),)
            sanitized_item = self._sanitize(item, item_path)
            sanitized_list.append(sanitized_item)
        return sanitized_list

    def _sanitize_string(self, obj: str, path_tuple: tuple[str, ...]) -> str:
        """Sanitize a string value that contains secrets."""
        if self._is_secret_key(path_tuple[-1], obj):
            match = self._bearer_regex.match(obj)
            self._mark_leak(path_tuple)
            if match:
                return f"{match.group('scheme')}<REDACTED>"
            return "<REDACTED>"
        return obj

    def _is_secret_key(self, key: str, value: Optional[str]) -> bool:
        """
        Check if a key-value pair indicates a secret.

        Args:
            key: The configuration key
            value: The configuration value

        Returns:
            True if the key indicates a secret and value is not an environment variable
        """
        key_is_secret_key = any(secret_key in key.lower() for secret_key in self._secret_key_tokens)
        if isinstance(value, str):
            match = utils_configurations.ENVIRONMENT_VARIABLE_REGEX.search(value)
            value_is_environment_variable = match is not None
            return key_is_secret_key and not value_is_environment_variable

        return key_is_secret_key

    def _mark_leak(self, path: tuple[str, ...]) -> None:
        """Mark a path as containing a leaked secret."""
        self.leaks.append(".".join(path))
