from selectolax.parser import HTMLParser
from items import Company
from scrapy.loader import ItemLoader

from urllib.parse import urljoin

from typing import *

import scrapy

LINK_US = "https://www.value.today/headquarters/united-states-america-usa?page={}"
LINK_CHINA = "https://www.value.today/headquarters/china?page={}"


class CompaniesSpider(scrapy.Spider):
    name = "value_today"
    base_url = "https://www.value.today/"

    custom_settings = {"LOG_LEVEL": "INFO"}

    country_link = LINK_CHINA

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self) -> scrapy.Request:
        for i in range(100):
            yield scrapy.Request(
                url=self.country_link.format(i), callback=self.parse_page
            )

    def parse_page(self, response) -> scrapy.Request:
        dom = HTMLParser(response.body)
        hrefs = [
            el.attributes["href"]
            for el in dom.css("div.item-list > ol > li div.group-header h1 > a")
        ]

        for href in hrefs:
            yield scrapy.Request(
                url=urljoin(self.base_url, href),
                callback=self.parse_company,
            )

    def parse_company(self, response):
        data = {}
        loader = ItemLoader(item=Company())

        dom = HTMLParser(response.body)

        header = dom.css_first("div.region-content > div > div.group-header")
        data["company_name"] = header.css_first("div:nth-child(1) > h1").text().strip()

        header_data = {
            name.text(): value.text()
            for name, value in zip(
                header.css("div:nth-child(n+2) > div.field--label"),
                header.css("div:nth-child(n+2) > div.field--item"),
            )
        }

        data.update(header_data)

        for selector in ["div.group-left", "div.group-right"]:
            side = dom.css(f"div.region-content > div > {selector} > div")

            side_data = {}

            for div in side:
                name = div.css_first("div.field--label")
                if not name:  # check if name is None else skip to the next
                    continue
                name = name.text()
                if items := div.css_first("div.field--items"):
                    side_data[name] = [
                        item.text() for item in items.css("div.field--item")
                    ]
                else:
                    side_data[name] = div.css_first("div.field--item").text()

            data.update(side_data)

        mapping = {
            "company_name": "company_name",
            "World Rank (Jan-07-2022)": "world_rank_2022",
            "World Rank (Sep-01-2021)": "world_rank_2021",
            "World Rank (Jan-2020)": "world_rank_2020",
            "Market Cap (Jan-07-2022)": "mcap_2022",
            "Market Cap (Jan-01-2021)": "mcap_2021",
            "Market Cap (Jan 1st 2020)": "mcap_2020",
            "Annual Revenue in USD": "annual_revenue",
            "Annual Net Income in USD": "annual_net_income",
            "Total Assets in USD": "total_assets",
            "Total Liabilities in USD": "total_liabilities",
            "Total Equity in USD": "total_equity",
            "Company Business": "company_business",
            "Company Rank in Country in 2022": "local_rank_2022",
            "Rank in Country (Jan-2021)": "local_rank_2021",
            "Rank in Country (Jan-2020)": "local_rank_2020",
            "Number of Employees": "num_employees",
        }

        for key, val in mapping.items():
            loader.add_value(val, data[key] if key in data else None)

        yield loader.load_item()
