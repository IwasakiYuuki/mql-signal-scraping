class SignalStats:

    def __init__(self, **stats):
        self.stats = stats

    def record(self) -> dict:
        return self.stats

    @classmethod
    def from_record(cls, record: dict):
        return cls(**record)
