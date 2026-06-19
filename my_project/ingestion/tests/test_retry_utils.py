import pytest
from unittest.mock import MagicMock, patch
from ingest_book import handle_api_call_with_retry


class TestHandleApiCallWithRetry:
    def test_succeeds_first_attempt(self):
        func = MagicMock(return_value="success")
        result = handle_api_call_with_retry(func, max_retries=3)
        assert result == "success"
        assert func.call_count == 1

    def test_succeeds_after_retry(self):
        func = MagicMock(side_effect=[Exception("fail"), "success"])
        result = handle_api_call_with_retry(func, max_retries=3)
        assert result == "success"
        assert func.call_count == 2

    def test_fails_all_retries(self):
        func = MagicMock(side_effect=Exception("always fails"))
        with pytest.raises(Exception, match="always fails"):
            handle_api_call_with_retry(func, max_retries=3)
        assert func.call_count == 3
