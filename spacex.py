#!/usr/bin/env python3

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import argparse
import json
import logging
import os
import requests
import sys


class HttpClient:
    def __init__(self):
        self.session = Session()
        retries = Retry(
            total=1,  # one retry
            backoff_factor=15,  # waits 15 seconds for second try
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get(self, url):
        try:
            response = self.session.get(
                url,
                timeout=15,  # 15 seconds of timeout
            )
            if response.status_code < 200 or response.status_code > 299:  # duplicates "except Exception" but I left it for the exercise purposes
                logging.critical(f"HTTP GET response error, status code: {response.status_code}")
                sys.exit(1)
            response.raise_for_status()
            return response
        except requests.exceptions.RetryError:
            logging.critical(f"HTTP GET retry limit reached")
            sys.exit(1)
        except Exception as e:
            logging.critical(f"HTTP GET unknown error: {e}")
            sys.exit(1)


class SpaceXApp:
    def __init__(self, action, refresh, cache):
        self.action = action
        self.refresh = refresh
        self.cache = cache
        self.client = HttpClient()

    def get_launches(self):
        # cache file refresh
        if os.path.exists(self.cache) and self.refresh:
            logging.debug(f"deleting cache file")
            os.remove(self.cache)

        # use cache file if exists
        if os.path.exists(self.cache):
            logging.debug(f"using cache file")
            with open(self.cache, "r", encoding="utf-8") as file:
                launches = json.load(file)
                logging.debug(f"local launches count: {len(launches)}")
                return launches

        # download remote content
        response = self.client.get("https://api.spacexdata.com/v4/launches")
        launches = response.json()
        logging.debug(f"remote launches count: {len(launches)}")
        with open(self.cache, "w", encoding="utf-8") as file:
            json.dump(launches, file, indent=2)
        return launches

    def report_action(self):
        launches = self.get_launches()

        report_year = 2022
        total_launches = 0
        successful_launches = 0
        failed_launches = 0
        for launch in launches:
            if not "date_utc" in launch:
                raise Exception("launch date_utc field not found")
            if not launch["date_utc"].startswith(f"{report_year}-"):
                continue  # skip entries from another years

            total_launches += 1
            if "success" in launch:
                if launch["success"] == True:
                    successful_launches += 1
                elif launch["success"] == False:
                    failed_launches += 1

        success_ratio = successful_launches / (successful_launches + failed_launches) * 100

        print(f"Year {report_year} summary:")
        print(f"Total: {total_launches} | Successful: {successful_launches} | Failed: {failed_launches} | Success ratio: {success_ratio:.2f}%")

    def payloads_action(self):
        launches = self.get_launches()

        counts = []
        for launch in launches:
            if not "payloads" in launch:
                counts.append(0)
                continue
            counts.append(len(launch["payloads"]))

        average_payload_count = sum(counts) / len(launches)

        print(f"Average payloads per launch: {average_payload_count:.2f}")

    def launchpads_action(self):
        launches = self.get_launches()

        counts = {}
        for launch in launches:
            launchpad = "unknown"
            if "launchpad" in launch:
                launchpad = launch["launchpad"]

            if not launchpad in counts:
                counts[launchpad] = 0
            counts[launchpad] += 1

        print("Count of launches per launchpad ID:")
        for launchpad, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            print(f"- {launchpad} - {count}")

    def run(self):
        if self.action == "report":
            self.report_action()
        elif self.action == "payloads":
            self.payloads_action()
        elif self.action == "launchpads":
            self.launchpads_action()
        else:
            print(f"unknown action: {self.action}")


def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, help="report, payloads or launchpads", required=True)
    parser.add_argument("-v", "--verbose",  action="store_true", help="increases logging detail", required=False)
    parser.add_argument("--refresh", action="store_true", help="ignores cache and refetches from API", required=False)
    parser.add_argument("--cache", type=str, help="path to cache file", required=False, default="launches.json")
    args = parser.parse_args()

    # setup basic logger
    logging.basicConfig(
        format="%(levelname)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    # run app
    logging.debug(f"args: {args}")
    spacex_app = SpaceXApp(args.action, args.refresh, args.cache)
    spacex_app.run()
    logging.debug("done.")


if __name__ == "__main__":
    main()
