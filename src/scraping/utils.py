import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def waf_element(driver: WebDriver | WebElement, value: str, by: str = By.XPATH) -> WebElement:
    """Wait until find element"""
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
    # Temporary, remove waiting
    # return driver.find_element(by, value)

def waf_elements(driver: WebDriver | WebElement, value: str, by: str = By.XPATH) -> list[WebElement]:
    """Wait until find elements"""
    return WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((by, value)))
    # Temporary, remove waiting
    # return driver.find_elements(by, value)

def extract_float(text: str) -> float:
    """Extracts a float from a text string

    If the float is formatted with spaces, they are removed
    If the integer is not a number, return 0.0

    Args:
        text (str): Text with a float

    Returns:
        float: The extracted Float

    Raises:
        ValueError: If the float is not found in the text
    
    Example:
        >>> extract_float("Total: 1 234.56")
        1234.56
    """
    match = re.search(r"(\d{1,3}(?:\s\d{3})*(?:\.\d+)?)", text)
    if not match:
        if "n/a" in text:
            return 0.0
        raise ValueError(f"Float not found in {text}")
    return float(match.group(1).replace(" ", ""))

def extract_int(text: str) -> int:
    """Extracts an integer from a text string

    If the integer is formatted with spaces, they are removed
    If the integer is not a number, return 0

    Args:
        text (str): Text with an integer

    Returns:
        int: The extracted Integer

    Raises:
        ValueError: If the integer is not found in the text
    
    Example:
        >>> extract_int("Total: 1 234")
        1234
    """
    match = re.search(r"(\d{1,3}(?:\s\d{3})*)", text)
    if not match:
        if "n/a" in text:
            return 0
        raise ValueError(f"Integer not found in {text}")
    return int(match.group(1).replace(" ", ""))

def extract_time(text: str) -> int:
    """Extracts a time from a text string

    Able to recognize multiple units of time, all converted to numerical values in minutes and return values.
    The corresponding units are "year", "day", "hour", and "minute".
    """
    time_units = {
        "year": 525600,
        "day": 1440,
        "hour": 60,
        "minute": 1
    }
    time = 0
    for unit, value in time_units.items():
        match = re.search(r"(\d+)\s"+unit, text)
        if match:
            time += int(match.group(1)) * value
    return time

def parse_value(value):
    time_units = {
        "minutes": 1,
        "hours": 60,
        "days": 1440
    }

    def convert_to_minutes(time_str):
        for unit, multiplier in time_units.items():
            if unit in time_str:
                number = re.findall(r"\d+", time_str)
                if number:
                    return int(number[0]) * multiplier
        return None

    number_match = re.search(r"-?\d+\.?\d*", value)
    number = float(number_match.group(0)) if number_match else None

    if any(unit in value for unit in time_units):
        number = convert_to_minutes(value)

    return number
