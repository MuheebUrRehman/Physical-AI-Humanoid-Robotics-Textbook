import re
from typing import Optional

def _strip_control_chars(text: str) -> str:
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

def validate_query(query: str) -> tuple[bool, Optional[str], str]:
    """
    Validate and sanitize user query for the RAG chatbot.

    Args:
        query: The user's query string

    Returns:
        Tuple of (is_valid, error_message, sanitized_query)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty", query

    if len(query.strip()) < 3:
        return False, "Query must be at least 3 characters long", query

    if len(query) > 2000:
        return False, "Query exceeds maximum length of 2000 characters", query

    # Check for potentially harmful patterns against original query
    harmful_patterns = [
        r'<script',  # Potential XSS
        r'javascript:',  # Potential XSS
        r'vbscript:',  # Potential XSS
        r'on\w+\s*=',  # Potential XSS
        r'eval\s*\(',  # Potential code execution
        r'exec\s*\(',  # Potential code execution
        r'os\.system\s*\(',  # Potential OS command (not bare 'os.')
        r'subprocess\.',  # Potential subprocess execution
        r'(\.\.\/)+',  # Directory traversal
    ]

    for pattern in harmful_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False, "Query contains potentially harmful content", query

    # Additional check: look for SQL injection patterns (only dangerous constructs)
    sql_patterns = [
        r"(\'\s*(OR|AND)\s*\'\s*=\s*\'\s*)",
        r"(;\s*(DROP|EXEC|CALL|ALTER)\s+)",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False, "Query contains potentially harmful SQL content", query

    # Sanitize: strip control characters that could interfere with LLM processing
    sanitized_query = _strip_control_chars(query)

    return True, None, sanitized_query


def validate_user_id(user_id: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate user ID if provided with enhanced security.

    Args:
        user_id: Optional user identifier

    Returns:
        Tuple of (is_valid, error_message)
    """
    if user_id is None:
        return True, None

    if not user_id.strip():
        return False, "User ID cannot be empty"

    if len(user_id) > 100:
        return False, "User ID exceeds maximum length of 100 characters"

    # Only allow alphanumeric characters, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        return False, "User ID contains invalid characters. Only alphanumeric characters, hyphens, and underscores are allowed."

    # Additional check for potential path traversal or other attacks
    if '..' in user_id or '/' in user_id or '\\' in user_id:
        return False, "User ID contains invalid characters that could be used for path traversal."

    return True, None


def validate_session_id(session_id: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate session ID if provided with enhanced security.

    Args:
        session_id: Optional session identifier

    Returns:
        Tuple of (is_valid, error_message)
    """
    if session_id is None:
        return True, None

    if not session_id.strip():
        return False, "Session ID cannot be empty"

    if len(session_id) > 100:
        return False, "Session ID exceeds maximum length of 100 characters"

    # Only allow alphanumeric characters, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        return False, "Session ID contains invalid characters. Only alphanumeric characters, hyphens, and underscores are allowed."

    # Additional check for potential path traversal or other attacks
    if '..' in session_id or '/' in session_id or '\\' in session_id:
        return False, "Session ID contains invalid characters that could be used for path traversal."

    return True, None
