from spider import BlockChainSpider
from tqdm import tqdm
from typing import *

import json
import sys

# --------------------------------------------------------------
# Given companies slugs collect data from BlockData website
# Script grabs slugs from slugs folder
# $python scrapers/blockdata/data.py us/china to collect data from slugs
# --------------------------------------------------------------

configs = {
    "china": {
        "OUTPUT_URI": "data/blockdata/blockchain_china.json",
        "READ_URI": "scrapers/blockdata/slugs/slugs_china.json",
    },
    "us": {
        "OUTPUT_URI": "data/blockdata/blockchain_us.json",
        "READ_URI": "scrapers/blockdata/slugs/slugs_us.json",
    },
}


def load_blockchain_matches(slugs_uri: str) -> List[dict]:
    with open(slugs_uri, "r") as file:
        return json.load(file)


def main() -> None:
    blockdata = []

    OURPUT_URI, READ_URI = configs[sys.argv[1]].values()

    data = load_blockchain_matches(READ_URI)
    block = BlockChainSpider()

    for match in tqdm(data):
        status, n_articles, tier = False, 0, 0
        use_cases = []

        for el in match["search_res"]:
            resp: Dict[str, Any] = block.query_company(el["slug"])

            if resp["status"] == "Active":
                status = True

            n_articles += resp["total_news_articles"]

            if resp["tier"]:
                if resp["tier"] > tier:
                    tier = resp["tier"]

            if resp["usecases"]:
                use_cases.extend(resp["usecases"])

        blockdata.append(
            {
                "company_name": match["company"],
                "status": status,
                "use_cases": use_cases,
                "slugs_matched": [el["slug"] for el in match["search_res"]],
                "related_companies": [el["name"] for el in match["search_res"]],
                "total_articles": n_articles,
                "profile_tier": tier,
            }
        )

    with open(OURPUT_URI, "w") as file:
        json.dump(blockdata, file)


if __name__ == "__main__":
    main()
