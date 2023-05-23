import json
import sys
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tqdm import tqdm
from typing import *


class LinkExtractor:
    def __init__(self, output_loc: str) -> Self:
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get("https://www.marketscreener.com/")
        self.load_companies()
        self.file = open(output_loc, "a", encoding="utf8")
        self.file.write("[")

    def load_companies(self) -> None:
        with open("data/companies/companies_china.json", "r") as file:
            self.companies: List[str] = [el["company_name"] for el in json.load(file)]

    def locate_element_by_css(self, selector: str) -> WebElement:
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def collect_links(self) -> None:
        input(
            "Make sure to close all popups and log into account. Then press anything:"
        )
        search_bar: WebElement = self.locate_element_by_css(
            "input[data-submit-form='recherche_menu']"
        )
        for company in tqdm(self.companies):
            search_bar.send_keys(company)
            # make sure there is no StaleElementException when accessing attributes of unloaded element
            time.sleep(2)
            try:
                first_match: WebElement = self.locate_element_by_css(
                    "table.table--hover tr.table-child--pointer > td > a"
                )
                data = {
                    "company_name": company,
                    "matched_to": first_match.text,
                    "url": first_match.get_attribute("href"),
                }
                json.dump(data, self.file, indent=4)

                self.file.write(",")

            except TimeoutException:
                continue

            search_bar.clear()

        self.file.write("]")


if __name__ == "__main__":
    link = LinkExtractor(sys.argv[1])
    link.collect_links()
