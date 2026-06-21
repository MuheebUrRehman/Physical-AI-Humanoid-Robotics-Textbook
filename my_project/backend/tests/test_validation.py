import pytest
from utils.validation import validate_query, validate_user_id, validate_session_id


class TestValidateQuery:
    def test_empty_query(self):
        is_valid, error, _ = validate_query("")
        assert is_valid is False
        assert error == "Query cannot be empty"

    def test_whitespace_only(self):
        is_valid, error, _ = validate_query("   ")
        assert is_valid is False

    def test_too_short(self):
        is_valid, error, _ = validate_query("ab")
        assert is_valid is False
        assert "at least 3" in error

    def test_too_long(self):
        is_valid, error, _ = validate_query("a" * 2001)
        assert is_valid is False
        assert "2000" in error

    def test_valid_query(self):
        is_valid, error, sanitized = validate_query("What is ROS 2?")
        assert is_valid is True
        assert error is None
        assert sanitized == "What is ROS 2?"

    def test_xss_script_tag(self):
        is_valid, error, _ = validate_query("<script>alert(1)</script>")
        assert is_valid is False

    def test_javascript_protocol(self):
        is_valid, error, _ = validate_query("javascript:alert(1)")
        assert is_valid is False

    def test_os_command_injection(self):
        is_valid, error, _ = validate_query("os.system('rm -rf /')")
        assert is_valid is False

    def test_path_traversal(self):
        is_valid, error, _ = validate_query("../../../etc/passwd")
        assert is_valid is False

    def test_legitimate_sql_question(self):
        is_valid, error, _ = validate_query("What does SELECT do in SQL?")
        assert is_valid is True
        assert error is None

    def test_legitimate_import_question(self):
        is_valid, error, _ = validate_query("How do I import numpy in Python?")
        assert is_valid is True
        assert error is None

    def test_dangerous_sql_injection(self):
        is_valid, error, _ = validate_query("'; DROP TABLE users; --")
        assert is_valid is False

    def test_control_chars_stripped(self):
        _, _, sanitized = validate_query("hello\x00world\x1f")
        assert "hello" in sanitized
        assert "world" in sanitized
        assert "\x00" not in sanitized
        assert "\x1f" not in sanitized


class TestValidateUserId:
    def test_none_is_valid(self):
        is_valid, error = validate_user_id(None)
        assert is_valid is True

    def test_valid_user_id(self):
        is_valid, error = validate_user_id("student-123")
        assert is_valid is True

    def test_empty_user_id(self):
        is_valid, error = validate_user_id("")
        assert is_valid is False

    def test_too_long(self):
        is_valid, error = validate_user_id("a" * 101)
        assert is_valid is False

    def test_invalid_chars(self):
        is_valid, error = validate_user_id("user@name!")
        assert is_valid is False

    def test_path_traversal_in_user_id(self):
        is_valid, error = validate_user_id("../../etc")
        assert is_valid is False


class TestValidateSessionId:
    def test_none_is_valid(self):
        is_valid, error = validate_session_id(None)
        assert is_valid is True

    def test_valid_session(self):
        is_valid, error = validate_session_id("session_ABC-123")
        assert is_valid is True

    def test_empty_session(self):
        is_valid, error = validate_session_id("")
        assert is_valid is False

    def test_invalid_chars(self):
        is_valid, error = validate_session_id("session id with spaces")
        assert is_valid is False


