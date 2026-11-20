"""Persistent monotonic sequence tracking."""
from app.database.db_manager import Database


class ReplayProtection:
    def __init__(self, database: Database) -> None:
        self.database = database

    def accept(self, device_id: str, sequence: int) -> bool:
        return self.database.accept_sequence(device_id, sequence)
