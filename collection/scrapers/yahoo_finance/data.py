import scrapy
import json
import random
import re
from datetime import datetime
from bs4 import BeautifulSoup

from urllib.parse import urlencode
from typing import *


class DataCollector(scrapy.Spider):
    name_map = {
        "annualTotalRevenue": "total_revenue",
        "annualBasicEPS": "basic_eps",
        "annualTotalAssets": "total_assets",
        "annualNetIncome": "net_income",
        "annualTotalLiabilitiesNetMinorityInterest": "total_liabilities",
        "annualTotalEquityGrossMinorityInterest": "total_equity",
        "annualInvestingCashFlow": "investing_cashflow",
        "annualTotalCapitalization": "total_capitalization",
    }
    name = "yahoo_data"

    custom_settings = {"LOG_LEVEL": "INFO"}

    # handle_httpstatus_list = [404]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_matched_companies()
        self.load_agents()
        self.load_headers()

    def load_matched_companies(self) -> None:
        with open("data/yahoo_finance/symbols/matches_us.json", "r") as file:
            self.companies = json.load(file)

    def load_headers(self) -> None:
        with open("scrapers/yahoo_finance/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def load_agents(self) -> None:
        with open("scrapers/yahoo_finance/cfg/user_agents.json", "r") as file:
            self.agents = json.load(file)["agents"]

    def start_requests(self):
        for company in self.companies:
            if company["matched_to"]:
                params = {
                    "lang": "en-US",
                    "region": "US",
                    "symbol": company["matched_symbol"],
                    "padTimeSeries": "true",
                    "type": ",".join(self.name_map.keys()),
                    "merge": "false",
                    "period1": 493590046,
                    "period2": 1682771124,
                    "corsDomain": "finance.yahoo.com",
                }
                self.headers["user-agent"] = random.choice(self.agents)

                yield scrapy.Request(
                    url="https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{}?{}".format(
                        company["matched_symbol"], urlencode(params)
                    ),
                    headers=self.headers,
                    callback=self.parse_financials,
                    meta={
                        "company_name": company["company_name"],
                        "matched_to": company["matched_to"],
                        "matched_symbol": company["matched_symbol"],
                    },
                )

    def parse_financials(self, response) -> scrapy.Request:
        resp = json.loads(response.body)

        data = {
            "company_name": response.meta["company_name"],
            "matched_to": response.meta["matched_to"],
        }
        currency = None

        for index in resp["timeseries"]["result"]:
            index_name = index["meta"]["type"][0]
            if index_name in self.name_map:
                if index_name in index:
                    for value in index[index_name]:
                        if value:
                            currency = value["currencyCode"]
                            year = datetime.strptime(value["asOfDate"], "%Y-%M-%d").year
                            reported_value = value["reportedValue"]["raw"]
                            if year in [2019, 2020, 2021, 2022]:
                                mapped_name = self.name_map[index_name]
                                data[f"{mapped_name}_{year}"] = reported_value

        data["currency"] = currency

        symbol = response.meta["matched_symbol"]

        yield scrapy.Request(
            url="https://finance.yahoo.com/quote/{}/profile?p={}".format(
                symbol, symbol
            ),
            headers=self.headers,
            callback=self.collect_workers,
            meta={"item": data},
        )

    def collect_workers(self, response) -> Dict[str, Any]:
        soup = BeautifulSoup(response.body, "html.parser")
        employees = soup.find("span", string=re.compile("Full Time Employees"))
        data = response.meta["item"]
        num_emp = None
        if employees:
            num_emp_str = employees.findNext().text
            if num_emp_str:  # check not ""
                num_emp = re.sub("[^\d]", "", num_emp_str)

        data["num_employees"] = num_emp

        yield data
