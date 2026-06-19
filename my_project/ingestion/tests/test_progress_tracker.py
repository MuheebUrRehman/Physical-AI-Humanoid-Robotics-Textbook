import pytest
from ingest_book import ProgressTracker


class TestProgressTracker:
    def test_initial_state(self):
        tracker = ProgressTracker(total_items=10, description="Testing")
        assert tracker.completed == 0
        assert tracker.total_items == 10

    def test_update_increments(self):
        tracker = ProgressTracker(total_items=5)
        tracker.update()
        assert tracker.completed == 1

    def test_multiple_updates(self):
        tracker = ProgressTracker(total_items=3)
        tracker.update()
        tracker.update(2)
        assert tracker.completed == 3

    def test_complete(self, capsys):
        tracker = ProgressTracker(total_items=1, description="Test")
        tracker.update()
        tracker.complete()
        captured = capsys.readouterr()
        assert "100%" in captured.out
