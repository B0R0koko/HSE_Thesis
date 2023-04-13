import json
import scrapy
import re

from scrapy.loader import ItemLoader
from urllib.parse import urlencode

from items import Financials

from typing import *


def prepare_for_search(company: str) -> str:
    company = re.sub("CORPORATION", "CORP", company)
    company = re.sub("COMPANY", "CO", company)
    company = re.sub("[^\w\s]", "", company)
    company = re.sub(",{0,1} INC", "", company)
    company = re.sub("\(.*?\)", "", company)
    return company


class MorningStarSpider(scrapy.Spider):
    name = "morningstar"

    custom_settings = {"LOG_LEVEL": "INFO"}

    financial_api_link = "https://api-global.morningstar.com/sal-service/v1/stock/newfinancials/{}/annual/summary?{}"

    def __init__(self, **kwargs) -> Self:
        super().__init__(**kwargs)
        self.load_companies()
        self.load_headers()

    def load_companies(self) -> None:
        with open("data/companies/companies_us.json", "r") as file:
            data = json.load(file)
            self.companies = [company["company_name"] for company in data]

    def load_headers(self) -> None:
        with open("scrapers/financials/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    # make an initial request to api endpoint to find security_id of the company
    def start_requests(self) -> scrapy.Request:
        for company in self.companies:
            params = {
                "q": prepare_for_search(company),
                "limit": "6",
                "autocomplete": "true",
            }

            yield scrapy.Request(
                method="GET",
                url=f"https://www.morningstar.com/api/v1/search/securities?{urlencode(params)}",
                headers=self.headers,
                callback=self.parse,
                meta={"company": company},
            )

    # query second time to get financial data based on security id
    def parse(self, response) -> scrapy.Request:
        resp = json.loads(response.body)
        company = response.meta["company"]

        params = {
            "reportType": "A",
            "languageId": "en",
            "locale": "en",
            "clientId": "MDC",
            "component": "sal-components-equity-financials-summary",
            "version": "3.79.0",
        }

        if resp["results"]:
            yield scrapy.Request(
                url=self.financial_api_link.format(
                    resp["results"][0]["secId"], urlencode(params)
                ),
                method="GET",
                headers=self.headers,
                callback=self.parse_financials,
                meta={"company": company, "matched_to": resp["results"][0]["name"]},
            )

    def parse_financials(self, response) -> Dict[str, Any]:
        resp = json.loads(response.body)

        loader = ItemLoader(item=Financials())

        loader.add_value("company_name", response.meta["company"])
        loader.add_value("matched_to", response.meta["matched_to"])

        desired_financials = [
            "norm_eps_2022",
            "norm_eps_2021",
            "norm_eps_2020",
            "norm_eps_2019",
            "cashflow_investing_2022",
            "cashflow_investing_2021",
            "cashflow_investing_2020",
            "cashflow_investing_2019",
        ]

        for financial in desired_financials:
            loader.add_value(financial, resp)

        yield loader.load_item()
