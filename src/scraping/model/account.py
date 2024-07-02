import ast
import pandas as pd


class SignalAccount:

    def __init__(
        self,
        growth_total: float,
        growth_ave: float,
        deposit: float,
        withdrawal: float,
        growth_table: pd.DataFrame | str,
    ):
        self.growth_total = growth_total
        self.growth_ave = growth_ave
        self.deposit = deposit
        self.withdrawal = withdrawal
        self.growth_table = self.format_growth_table(growth_table)

    def record(self) -> dict:
        return {
            "growth_total": self.growth_total,
            "growth_ave": self.growth_ave,
            "deposit": self.deposit,
            "withdrawal": self.withdrawal,
            "growth_table": self.growth_table.to_records(index=True),
        }

    def get_growth_table(self):
        return self.growth_table

    def format_growth_table(self, value):
        columns = [
            "year",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        if isinstance(value, pd.DataFrame):
            return value
        elif isinstance(value, str):
            value = value.replace("\n", ",")
            value = ast.literal_eval(value)
            df = pd.DataFrame(value)
            df.columns = columns
            df.set_index("year", inplace=True)
            return df
        else:
            raise TypeError(f"Not supported type: {type(value)}")
