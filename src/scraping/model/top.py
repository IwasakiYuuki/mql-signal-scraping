class SignalTop:

    def __init__(
        self,
        name: str,
        author: str,
        rating: float,
        rating_num: int,
        reliability: int,
        week: int,
        subscriber_num: int,
        subscriber_funds: int,
        currency: str,
    ):
        self.name = name
        self.author = author
        self.rating = rating
        self.rating_num = rating_num
        self.reliability = reliability
        self.week = week
        self.subscriber_num = subscriber_num
        self.subscriber_funds = subscriber_funds
        self.currency = currency

    def record(self) -> dict:
        return {
            "name": self.name,
            "author": self.author,
            "rating": self.rating,
            "rating_num": self.rating_num,
            "reliability": self.reliability,
            "week": self.week,
            "subscriber_num": self.subscriber_num,
            "subscriber_funds": self.subscriber_funds,
            "currency": self.currency,
        }

    @classmethod
    def from_record(cls, record: dict):
        return cls(
            name=record["name"],
            author=record["author"],
            rating=record["rating"],
            rating_num=record["rating_num"],
            reliability=record["reliability"],
            week=record["week"],
            subscriber_num=record["subscriber_num"],
            subscriber_funds=record["subscriber_funds"],
            currency=record["currency"],
        )
