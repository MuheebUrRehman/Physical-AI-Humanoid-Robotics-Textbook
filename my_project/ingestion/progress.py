import logging

class ProgressTracker:
    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.description = description
        self.completed = 0
        self.logger = logging.getLogger(__name__)

    def update(self, increment: int = 1, message: str = ""):
        self.completed += increment
        percentage = (self.completed / self.total_items) * 100
        status_message = f"{self.description}: {self.completed}/{self.total_items} ({percentage:.1f}%)"
        if message:
            status_message += f" - {message}"
        self.logger.info(status_message)
        print(status_message)

    def complete(self):
        self.logger.info(f"{self.description} completed successfully")
        print(f"{self.description} completed: 100%")
