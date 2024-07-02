class SignalStats:

    def __init__(self, **stats):
        self.stats = stats

    def record(self) -> dict:
        return self.stats
