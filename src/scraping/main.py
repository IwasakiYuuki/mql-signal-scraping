import time
from pathlib import Path

import pandas as pd
from typer import Typer
from selenium import webdriver
from selenium.webdriver.common.by import By

from scraping.scraper import SignalScrapper
from scraping.utils import waf_elements

app = Typer()


def get_signal_links(driver: webdriver.Chrome, limit: int) -> list[str]:
    signal_links = []
    i = 1
    while True:
        driver.get(f"https://www.mql5.com/en/signals/mt5/page{i}")
        if "404" in driver.title:
            break
        signal_a_elements = waf_elements(driver, "a.signal-card__wrapper", by=By.CSS_SELECTOR)
        _signal_links = [a.get_attribute('href') for a in signal_a_elements][:limit]
        _signal_links = [link for link in _signal_links if link is not None]
        signal_links += _signal_links
        if len(signal_links) >= limit:
            break
        i += 1
        time.sleep(20)
    return signal_links[:limit]

def scraping_signals(driver, signal_links, output_path):
    ss = SignalScrapper(driver)
    signals = ss.scrape(signal_links, output_path=output_path)
    records = [signal.record() for signal in signals]
    return pd.DataFrame.from_records(records)

@app.command()
def main(
    limit: int = 3,
    output_dat_path: Path = Path("output.dat"),
    output_csv_path: Path = Path("output.csv"),
):

    if output_dat_path.exists():
        raise FileExistsError(f"{output_dat_path} already exists.")

    options = webdriver.ChromeOptions()
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options)
    signal_links = get_signal_links(driver, limit)
    signals = scraping_signals(driver, signal_links, output_dat_path)
    signals.to_csv(f"{output_csv_path}", index=False)

if __name__ == "__main__":
    app()
