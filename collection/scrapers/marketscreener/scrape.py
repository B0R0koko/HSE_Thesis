from selectolax.parser import HTMLParser
import scrapy
import json

from utils import MAPPING_TO_FUNC, clear_value

from typing import *


class MarketScreener(scrapy.Spider):
    name = "marketscreener"

    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(self, **kwargs) -> Self:
        super().__init__(**kwargs)
        self.load_urls()

    def load_urls(self) -> None:
        with open("data/marketscreener/urls_china.json", "r") as file:
            self.urls: Dict[str, str] = {
                el["company_name"]: el["url"] for el in json.load(file)
            }

    def start_requests(self) -> scrapy.Request:
        for company_name, url in self.urls.items():
            yield scrapy.Request(
                url=url + "/financials/",
                callback=self.parse_financials,
                meta={"company_name": company_name},
            )

    def parse_financials(self, response) -> Dict[str, Any]:
        dom = HTMLParser(response.body)

        table_ids = ["Tableau_Histo_Valo", "Tableau_Histo_ECR_a", "Tableau_Histo_ECR_q"]
        data = {"company_name": response.meta["company_name"]}

        for table_id in table_ids:
            table = dom.css_first(f"div#{table_id} > table > tbody")

            rows = table.css("tr")

            mappings: Dict[str, Callable] = {
                el.css_first("sup").text(): MAPPING_TO_FUNC[el.text()[2:]]
                for el in rows[-2].css_first("td").css("div")
            }

            years = [el.text() for el in rows[0].css("td")[1:]]

            for row in rows[1:-2]:
                cols = row.css("td")
                row_name, flag = cols[0].text(), None

                if cols[0].css_first("sup"):
                    row_name, flag = cols[0].text()[:-1], cols[0].text()[-1]

                values = [clear_value(col.text()) for col in cols[1:]]

                for year, value in zip(years, values):
                    data[f"{row_name}_{year}"] = (
                        mappings[flag](value) if flag and value else value
                    )

        yield data
