from .top import SignalTop
from .account import SignalAccount
from .stats import SignalStats


class Signal:

    def __init__(
        self,
        top: SignalTop,
        account: SignalAccount,
        stats: SignalStats
    ):
        self.top = top
        self.account = account
        self.stats = stats

    def record(self) -> dict:
        return {
            **self.top.record(),
            **self.account.record(),
            **self.stats.record(),
        }

    def get_growth_table(self):
        return self.account.growth_table

    @classmethod
    def from_record(cls, record: dict):
        top = SignalTop.from_record(record)
        account = SignalAccount.from_record(record)
        stats = SignalStats.from_record(record)
        return cls(top, account, stats)
