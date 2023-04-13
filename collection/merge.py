import os
import pandas as pd
import sys


BASE_DIR = os.getcwd()

os.chdir(os.path.join(BASE_DIR, "data"))


def merge_companies() -> pd.DataFrame:
    df = pd.DataFrame()
    for file in os.listdir("companies"):
        df = pd.concat([df, pd.read_json(f"companies/{file}")])
        df["country"] = file.split("_")[-1]
    return df


def merge_blockdata() -> pd.DataFrame:
    df = pd.DataFrame()
    for file in os.listdir("blockdata"):
        df = pd.concat([df, pd.read_json(f"blockdata/{file}")])
    return df


def merge_financials() -> pd.DataFrame:
    df = pd.DataFrame()
    for file in os.listdir("financials"):
        df = pd.concat([df, pd.read_json(f"financials/{file}")])
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

    # output to sys.argv[1] location
    df_merged.to_csv(sys.argv[1], index=False)


if __name__ == "__main__":
    main()
