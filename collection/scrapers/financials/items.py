import scrapy

from itemloaders.processors import MapCompose, TakeFirst

from typing import *


MAGNITUDE_MAP = {"Billion": 10**9, "Million": 10**6}
CNY_DOLLAR = 0.14


def parse_eps(value: dict, year: str) -> Union[float, None]:
    income_statement = value["incomeStatement"]
    if income_statement["_meta"]["periodReport"] == "Success":
        years = income_statement["columnDefs"]
        for row in income_statement["rows"]:
            if row["label"] == "Normalized EPS":
                eps_data = dict(zip(years, row["datum"]))
                if year in eps_data:
                    return eps_data[year]
                return None
    return None


# returns cashflow from investing in dollars
def parse_cashflow(value: dict, year: str) -> Union[float, None]:
    cashflow = value["cashFlow"]
    if cashflow["_meta"]["periodReport"] == "Success":
        years = cashflow["columnDefs"]
        footer = cashflow["footer"]
        for row in cashflow["rows"]:
            if row["label"] == "Cash Flow from Investing Activities":
                cashflow_data = dict(zip(years, row["datum"]))
                if year in cashflow_data:
                    cashflow_value = cashflow_data[year]
                    if cashflow_value:
                        cashflow_value = (
                            float(cashflow_data[year])
                            * MAGNITUDE_MAP[footer["orderOfMagnitude"]]
                        )
                        if footer["currency"] == "CNY":
                            cashflow_value *= CNY_DOLLAR
                    return cashflow_value
                return None
    return None


class Financials(scrapy.Item):
    company_name = scrapy.Field(
        input_processor=MapCompose(), output_processor=TakeFirst()
    )
    matched_to = scrapy.Field(
        input_processor=MapCompose(), output_processor=TakeFirst()
    )
    norm_eps_2022 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_eps(x, "TTM")),
        output_processor=TakeFirst(),
    )
    norm_eps_2021 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_eps(x, "2021")),
        output_processor=TakeFirst(),
    )
    norm_eps_2020 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_eps(x, "2020")),
        output_processor=TakeFirst(),
    )
    norm_eps_2019 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_eps(x, "2019")),
        output_processor=TakeFirst(),
    )
    cashflow_investing_2022 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_cashflow(x, "TTM")),
        output_processor=TakeFirst(),
    )
    cashflow_investing_2021 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_cashflow(x, "2021")),
        output_processor=TakeFirst(),
    )
    cashflow_investing_2020 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_cashflow(x, "2020")),
        output_processor=TakeFirst(),
    )
    cashflow_investing_2019 = scrapy.Field(
        input_processor=MapCompose(lambda x: parse_cashflow(x, "2019")),
        output_processor=TakeFirst(),
    )
