import re

from typing import *


def clear_value(value):
    if value == "-":
        return None

    value = re.sub(",", ".", re.sub("[^\d\,\./]", "", value))

    if "." in value:
        return float(value)

    if "/" in value:
        return value

    return int(value)


def transform_1_mil_cny_to_billion_usd(value):
    RATE = 0.18
    return int(value) * RATE / 1000


def transform_cny_to_usd(value):
    RATE = 0.18
    return float(value) * RATE


def transform_mil_usd_to_buillion_usd(value):
    return int(value) / 1000


def transform_usd_to_usd(value):
    return float(value)


MAPPING_TO_FUNC = {
    "CNY in Million": transform_1_mil_cny_to_billion_usd,
    "CNY": transform_cny_to_usd,
    "USD in Million": transform_mil_usd_to_buillion_usd,
    "USD": transform_usd_to_usd,
}
