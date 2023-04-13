import requests
import json
import openai
import os

from typing import *


openai.api_key = os.environ.get("OPENAI_API_KEY")


class PersistedQueryError(Exception):
    pass


def handle_persisted_query(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PersistedQueryError:
            input("Refresh session key on the website. Press anything to continue: ")
            return wrapper(*args, **kwargs)

    return wrapper


class BlockChainSpider:
    def __init__(self) -> Self:
        self._load_headers()

    def _load_headers(self) -> None:
        with open("scrapers/blockdata/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def raise_for_error(self, resp: requests.Response) -> None:
        if "errors" in resp[0]:
            raise PersistedQueryError

    @handle_persisted_query
    def query_search(self, company: str) -> List[dict]:
        data = json.dumps(
            [
                {
                    "variables": {"searchTerm": company},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "e277b1b342de6ef8c679a527e2369f970bc64a13b016c5025833f67c35cb812c",
                        }
                    },
                }
            ]
        )

        resp = requests.post(
            "https://astronaut.blockdata.tech/graphql", data=data, headers=self.headers
        ).json()

        self.raise_for_error(resp)

        return resp[0]["data"]["search"]["results"]

    @handle_persisted_query
    def query_company(self, slug: str) -> Dict[str, Any]:
        data = json.dumps(
            [
                {
                    "operationName": "profile",
                    "variables": {"slug": slug, "authenticated": True},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "17adc6369a94622d0983aa421807a048f501f286e5fc4a5e13dcff488ba08b79",
                        }
                    },
                }
            ]
        )

        resp = requests.post(
            "https://astronaut.blockdata.tech/graphql", data=data, headers=self.headers
        ).json()

        self.raise_for_error(resp)

        return resp[0]["data"]["profile"]

    def check_relationship(self, matched: List[dict], matched_to: str) -> List[int]:
        companies = [el["name"] for el in matched]

        prompt = (
            f"Say true or false if companies listed below are related to {matched_to}.\n"
            f"Output results in this way: <company>: <true or false value> \n\n Companies: {companies}"
        )

        resp = openai.Completion.create(
            model="text-davinci-003", prompt=prompt, max_tokens=100, temperature=0
        )

        resp = resp["choices"][0]["text"].strip()

        matched_companies = []

        for i, el in enumerate(resp.split("\n")):
            _, is_related = el.split(": ", 1)
            if is_related == "True":
                matched_companies.append(i)

        return matched_companies

    def fetch_company(self, company: str) -> Dict[str, Any]:
        # split company name by spaces and search them adding more and more words
        split_words = company.split(" ")

        data = {"company": company, "search_res": []}

        for i in range(1, len(split_words) + 1):
            resp: List[dict] = self.query_search(" ".join(split_words[:i]))
            matched = [
                {"name": el["name"], "slug": el["slug"]}
                for el in resp[:5]
                if el["type"] == "Profiles"
            ]
            matched_indecies: List[int] = self.check_relationship(matched, company)
            if matched_indecies:
                data["search_res"] = [
                    el for i, el in enumerate(matched) if i in matched_indecies
                ]
                break

        return data


if __name__ == "__main__":
    block = BlockChainSpider()
    resp = block.fetch_company("Amazon")
