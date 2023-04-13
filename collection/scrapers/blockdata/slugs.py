from spider import BlockChainSpider
import json

from tqdm import tqdm

# -------------------------------------------------------------------
# Given companies names find their corresponding slugs on the website
# Script outputs matched slugs to slugs folder
# -------------------------------------------------------------------


DUMP_SLUGS_TO = "scrapers/blockdata/slugs/slugs_china.json"


def main() -> None:
    with open("data/companies/companies_china.json", "r") as file:
        data = json.load(file)

    companies = [el["name"] for el in data]

    block = BlockChainSpider()

    file = open(DUMP_SLUGS_TO, "a", encoding="utf8")
    file.write("[")

    try:
        for company in tqdm(companies):
            res = block.fetch_company(company)
            if res["search_res"]:
                json.dump(res, file, indent=4)
                file.write(",")
    except:
        raise

    finally:
        file.write("]")
        file.close()


if __name__ == "__main__":
    main()
