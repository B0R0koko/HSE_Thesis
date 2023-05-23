import os
import pandas as pd
import sys
import re


BASE_DIR = os.getcwd()

os.chdir(os.path.join(BASE_DIR, "data"))


def merge_companies() -> pd.DataFrame:
    df_m = pd.DataFrame()
    for file in os.listdir("companies"):
        df = pd.read_json(f"companies/{file}")
        df["country"] = re.search("_(.*?).json", file)[1]
        df_m = pd.concat([df_m, df])

    cols = [
        "company_name",
        "world_rank_2022",
        "world_rank_2021",
        "world_rank_2020",
        "company_business",
        "local_rank_2022",
        "local_rank_2021",
        "local_rank_2020",
        "num_employees",
        "founded_year",
        "ipo_year",
    ]
    return df_m[cols]


def merge_blockdata() -> pd.DataFrame:
    df = pd.DataFrame()
    for file in os.listdir("blockdata"):
        df = pd.concat([df, pd.read_json(f"blockdata/{file}")])
    return df


def merge_financials() -> pd.DataFrame:
    df = pd.DataFrame()
    for file in ["financials_us.json", "financials_china.json"]:
        df = pd.concat([df, pd.read_json(f"yahoo_finance/{file}")])

    return df


def main() -> None:
    # load datasets
    df_companies: pd.DataFrame = merge_companies()
    df_financials: pd.DataFrame = merge_financials()
    df_blockdata: pd.DataFrame = merge_blockdata()

    os.chdir(BASE_DIR)

    df_merged = pd.merge(
        df_companies,
        pd.merge(df_financials, df_blockdata, on="company_name", how="outer"),
        on="company_name",
        how="outer",
    )  # merge everything on company_name with outer overlapping

    df_merged = df_merged.convert_dtypes()
    # output to sys.argv[1] location
    df_merged.to_csv(sys.argv[1], index=False)


if __name__ == "__main__":
    main()
