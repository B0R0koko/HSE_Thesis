import scrapy
import json
import random

from urllib.parse import urlencode
from typing import *


class YahooLinkScraper(scrapy.Spider):
    name = "yahoo"

    custom_settings = {
        "LOG_LEVEL": "INFO",
        # "CONCURRENT_REQUESTS": 2,
        # "DOWNLOAD_DELAY": 4.5,
    }

    handle_httpstatus_list = [404]

    def __init__(self, **kwargs) -> Self:
        super().__init__(**kwargs)
        self.load_failed_companies()
        self.load_headers()
        self.load_agents()
        self.failed_companies = []

    def load_failed_companies(self) -> None:
        with open("scrapers/yahoo_finance/cfg/failed_companies.json", "r") as file:
            self.companies = json.load(file)["failed_companies"]

    def load_companies(self) -> None:
        with open("data/companies/companies_us.json", "r") as file:
            data = json.load(file)
            self.companies = [company["company_name"] for company in data]

    def load_headers(self) -> None:
        with open("scrapers/yahoo_finance/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def load_agents(self) -> None:
        with open("scrapers/yahoo_finance/cfg/user_agents.json", "r") as file:
            self.agents = json.load(file)["agents"]

    def start_requests(self) -> scrapy.Request:
        params = {
            "q": "SHANDONG GOLD MINING",
            "lang": "en-US",
            "region": "US",
            "quotesCount": 6,
            "newsCount": 2,
            "listsCount": 2,
            "enableFuzzyQuery": "false",
            "quotesQueryId": "tss_match_phrase_query",
            "multiQuoteQueryId": "multi_quote_single_token_query",
            "newsQueryId": "news_cie_vespa",
            "enableCb": "true",
            "enableNavLinks": "true",
            "enableEnhancedTrivialQuery": "true",
            "enableResearchReports": "true",
            "enableCulturalAssets": "true",
            "enableLogoUrl": "true",
            "researchReportsCount": 2,
        }

        for company in self.companies:
            params["q"] = company
            self.headers["user-agent"] = random.choice(self.agents)
            yield scrapy.Request(
                url=f"https://query1.finance.yahoo.com/v1/finance/search?{urlencode(params)}",
                headers=self.headers,
                callback=self.parse_matched_company,
                meta={"company_name": company},
            )

    def parse_matched_company(self, response) -> Dict[str, str]:
        if response.status == 404:
            self.failed_companies.append(response.meta["company_name"])
            return

        resp = json.loads(response.body)
        matched_company, matched_company_symbol = None, None

        if resp["quotes"]:
            first_match = resp["quotes"][0]
            matched_company_symbol = (
                first_match["symbol"] if "symbol" in first_match else None
            )
            matched_company = (
                first_match["longname"] if "longname" in first_match else None
            )

        yield {
            "company_name": response.meta["company_name"],
            "matched_to": matched_company,
            "matched_symbol": matched_company_symbol,
        }

    def closed(self, reason):
        with open("scrapers/yahoo_finance/cfg/failed_companies.json", "w") as file:
            json.dump({"failed_companies": self.failed_companies}, file)
