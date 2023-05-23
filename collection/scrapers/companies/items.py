import scrapy
import re

from itemloaders.processors import MapCompose, TakeFirst


def parse_money_vals(value):
    num = float(re.sub("[^\d\.]", "", value))
    if "Billion" in value:
        return num
    elif "Million" in value:
        return num / 1000


def parse_num_employees(value):
    return int(re.sub(",", "", value))


def parse_local_rank(value):
    return int(re.sub(",", "", value.split(" ")[-1]))


def parse_world_rank(value):
    return int(re.sub(",", "", value))


class Company(scrapy.Item):
    company_name = scrapy.Field(
        input_processor=MapCompose(), output_processor=TakeFirst()
    )
    # World rankings just take first value and load it
    world_rank_2022 = scrapy.Field(
        input_processor=MapCompose(parse_world_rank), output_processor=TakeFirst()
    )
    world_rank_2021 = scrapy.Field(
        input_processor=MapCompose(parse_world_rank), output_processor=TakeFirst()
    )
    world_rank_2020 = scrapy.Field(
        input_processor=MapCompose(parse_world_rank), output_processor=TakeFirst()
    )
    mcap_2022 = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    mcap_2021 = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    mcap_2020 = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    annual_revenue = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    annual_net_income = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    total_assets = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    total_liabilities = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    total_equity = scrapy.Field(
        input_processor=MapCompose(parse_money_vals),
        output_processor=TakeFirst(),
    )
    company_business = scrapy.Field()
    local_rank_2022 = scrapy.Field(
        input_processor=MapCompose(parse_local_rank),
        output_processor=TakeFirst(),
    )
    local_rank_2021 = scrapy.Field(
        input_processor=MapCompose(parse_local_rank),
        output_processor=TakeFirst(),
    )
    local_rank_2020 = scrapy.Field(
        input_processor=MapCompose(parse_local_rank),
        output_processor=TakeFirst(),
    )
    num_employees = scrapy.Field(
        input_processor=MapCompose(parse_num_employees),
        output_processor=TakeFirst(),
    )
    founded_year = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    ipo_year = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
