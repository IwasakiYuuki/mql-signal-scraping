import re

from tqdm import tqdm
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .model import (
    Signal,
    SignalTop,
    SignalAccount,
    SignalStats,
)
from .utils import extract_float, parse_value, waf_element, waf_elements


class SignalScrapper:

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def scrape(self, urls: list[str], close: bool = True) -> list[Signal]:
        signals = []
        for url in tqdm(urls):
            self._get(url)
            signals.append(self._scrape())
        if close:
            self._close()
        return signals

    def _scrape(self) -> Signal:
        top = self._scrape_top()
        account = self._scrape_account()
        stats = self._scrape_stats()
        return Signal(top=top, account=account, stats=stats)

    def _get(self, url: str):
        self.driver.get(url)

    def _close(self):
        self.driver.close()

    def _scrape_top(self) -> SignalTop:

        xpaths = {
            "name": "//div[@class='s-line-card__title']",
            "author": "//div[@class='s-line-card__author']",
            "rating": "//div[@class='s-line-card__rating rating-area']/div",
            "rating_num": "//div[@class='s-line-card__rating rating-area']",
            "reliability": "//div[@class='s-indicators__item s-indicators__item_risk']/div",
            "week": "//span[@class='s-indicators__item-desc s-indicators__item-desc_weeks']",
            "subscriber_num": "//div[@class='s-indicators__item-wrapper  s-indicators__item-wrapper_subscribers']/span[2]",
            "subscriber_funds": "//div[@class='s-indicators__item-wrapper  s-indicators__item-wrapper_subscribers']/span[3]",
            "currency": "//div[@class='chart-bar_horiz__value']",
        }

        def _format_rating(rating_str: str) -> float:
            rating = re.search(r"(\d+)", rating_str)
            if not rating:
                return 0.0
            return int(rating.group(1)) / 10

        def _format_rating_num(rating_num_str: str) -> int:
            rating_num = re.search(r"(\d+)", rating_num_str)
            if not rating_num:
                raise ValueError("Rating num not found")
            return int(rating_num.group(1))

        def _format_reliability(reliability_str: str) -> int:
            reliability = re.search(r"rel(\d)", reliability_str)
            if not reliability:
                raise ValueError("Reliability not found")
            return int(reliability.group(1))

        def _format_week(week_str: str) -> int:
            week = re.search(r"(\d+)", week_str)
            if not week:
                raise ValueError("Week not found")
            return int(week.group(1))

        def _format_subscriber_funds(subscriber_funds_str: str) -> int:
            subscriber_funds = re.search(r"(\d+[KM]*)", subscriber_funds_str)
            if not subscriber_funds:
                raise ValueError("Subscriber funds not found")
            if "K" in subscriber_funds.group(1):
                return int(float(subscriber_funds.group(1).replace("K", "")) * 1000)
            elif "M" in subscriber_funds.group(1):
                return int(float(subscriber_funds.group(1).replace("M", "")) * 1000000)
            else:
                return int(subscriber_funds.group(1))

        def _format_currency(currency_str: str) -> str:
            currency = re.search(r"(\w+)", currency_str)
            if not currency:
                raise ValueError("Currency not found")
            return currency.group(1)

        name = waf_element(self.driver, xpaths["name"]).text
        author = waf_element(self.driver, xpaths["author"]).text
        rating = _format_rating(waf_element(self.driver, xpaths["rating"]).get_attribute("class") or "")
        rating_num = _format_rating_num(waf_element(self.driver, xpaths["rating_num"]).text)
        reliability = _format_reliability(waf_element(self.driver, xpaths["reliability"]).get_attribute("class") or "")
        week = _format_week(waf_element(self.driver, xpaths["week"]).text)
        subscriber_num = int(waf_element(self.driver, xpaths["subscriber_num"]).text)
        subscriber_funds = _format_subscriber_funds(waf_element(self.driver, xpaths["subscriber_funds"]).text)
        currency = _format_currency(waf_element(self.driver, xpaths["currency"]).text)

        return SignalTop(
            name=name,
            author=author,
            rating=rating,
            rating_num=rating_num,
            reliability=reliability,
            week=week,
            subscriber_num=subscriber_num,
            subscriber_funds=subscriber_funds,
            currency=currency,
        )

    def _scrape_account(self) -> SignalAccount:

        def _get_growth_info(growth_chart: WebElement):
            header_divs = waf_elements(growth_chart, ".svg-chart__indicator-value", by=By.CSS_SELECTOR)
            header_divs = [waf_elements(div, "div", By.CSS_SELECTOR) for div in header_divs]
            growth_total = extract_float(header_divs[0][0].text)
            growth_ave = extract_float(header_divs[1][0].text)
            deposit = extract_float(header_divs[2][0].text) if len(header_divs) >= 3 else 0
            withdrawal = extract_float(header_divs[3][0].text) if len(header_divs) >= 4 else 0
            return growth_total, growth_ave, deposit, withdrawal

        def _get_growth_table(growth_chart: WebElement):
            table = waf_element(growth_chart, "table", by=By.CSS_SELECTOR)
            table_header_rows = waf_elements(table, "thead > tr", by=By.CSS_SELECTOR)
            table_body_rows = waf_elements(table, "tbody > tr", by=By.CSS_SELECTOR)
            header: list[str] = []
            for row in table_header_rows:
                th = waf_elements(row, "th", by=By.CSS_SELECTOR)
                header = [t.text for t in th]
            body: list[list[float]] = []
            for row in table_body_rows:
                td = waf_elements(row, "td", by=By.CSS_SELECTOR)
                body.append([float(t.text.replace("%", "") or 0) for t in td])
            table_df = pd.DataFrame(body)
            table_df.columns = header
            table_df.drop(columns=["Year"], inplace=True)
            table_df.rename(columns={"": "year"}, inplace=True)
            table_df.set_index("year", inplace=True)
            table_df.index = table_df.index.astype(int)
            return table_df

        growth_chart = waf_element(self.driver, "growth_chart", by=By.ID)
        growth_total, growth_ave, deposit, withdrawal = _get_growth_info(growth_chart)
        growth_table_df = _get_growth_table(growth_chart)

        return SignalAccount(
            growth_total=growth_total,
            growth_ave=growth_ave,
            deposit=deposit,
            withdrawal=withdrawal,
            growth_table=growth_table_df,
        )

    def _scrape_stats(self) -> SignalStats:

        stats_tab = waf_element(self.driver, "//li[@id='tab_stats']")
        self.driver.execute_script("arguments[0].click();", stats_tab)

        items = {
            "Trades:": "trades",
            "Profit Trades:": "profit_trades",
            "Loss Trades:": "loss_trades",
            "Best trade:": "best_trade",
            "Worst trade: ": "worst_trade",
            "Gross Profit:": "gross_profit",
            "Gross Loss:": "gross_loss",
            "Maximum consecutive wins:": "max_consecutive_wins",
            "Maximal consecutive profit:": "max_consecutive_profit",
            "Sharpe Ratio:": "sharpe_ratio",
            "Trading activity:": "trading_activity",
            "Max deposit load:": "max_deposit_load",
            "Latest trade:": "latest_trade",
            "Trades per week:": "trades_per_week",
            "Avg holding time:": "avg_holding_time",
            "Recovery Factor:": "recovery_factor",
            "Long Trades:": "long_trades",
            "Short Trades:": "short_trades",
            "Profit Factor:": "profit_factor",
            "Expected Payoff:": "expected_payoff",
            "Average Profit:": "average_profit",
            "Average Loss:": "average_loss",
            "Maximum consecutive losses:": "max_consecutive_losses",
            "Maximal consecutive loss:": "max_consecutive_loss",
            "Monthly growth:": "monthly_growth",
            "Annual Forecast:": "annual_forecast",
            "Algo trading:": "algo_trading",
            "Absolute": "drawdown_abs",
            "Maximal": "drawdown_max",
            "By Balance": "drawdown_rel_bal",
            "By Equity": "drawdown_rel_equ",
        }

        stats = {}

        for label, key in items.items():
            try:
                item_label_xpath = f"//div[contains(@class, 's-data-columns__label') and contains(text(), '{label}')]"
                item_value_xpath = f"./following-sibling::div[contains(@class, 's-data-columns__value')]"
                item_label = waf_element(self.driver, item_label_xpath)
                item_value = waf_element(item_label, item_value_xpath).text.strip()
                stats[key] = parse_value(item_value)
            except (NoSuchElementException, TimeoutException):
                stats[key] = None

        stats["pair"] = waf_element(self.driver, "//td[@class='col-symbol']").text

        return SignalStats(**stats)
