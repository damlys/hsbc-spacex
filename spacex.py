#!/usr/bin/env python3

from datetime import datetime
from src.http import HttpClient
import argparse
import json
import logging
import os


class SpaceXApp:
    def __init__(self, action, refresh, cache):
        self.action = action
        self.refresh = refresh
        self.cache = cache
        self.client = HttpClient()
        self.report_year = 2022

    def is_in_report_year(self, launch):
        if not "date_utc" in launch:
            return False  # date not present
        try:
            date = datetime.fromisoformat(launch["date_utc"])
            if date.year != self.report_year:
                return False
        except Exception as e:
            return False  # invalid date
        return True

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

        total_launches = 0
        successful_launches = 0
        failed_launches = 0
        for launch in launches:
            if not self.is_in_report_year(launch):
                continue

            total_launches += 1
            if "success" in launch:
                if launch["success"] == True:
                    successful_launches += 1
                elif launch["success"] == False:
                    failed_launches += 1

        success_ratio = successful_launches / (successful_launches + failed_launches) * 100

        print(f"Year {self.report_year} summary:")
        print(f"Total: {total_launches} | Successful: {successful_launches} | Failed: {failed_launches} | Success ratio: {success_ratio:.2f}%")

    def payloads_action(self):
        launches = self.get_launches()

        counts = []
        for launch in launches:
            if not self.is_in_report_year(launch):
                continue

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
            if not self.is_in_report_year(launch):
                continue

            launchpad = launch["launchpad"] if "launchpad" in launch else "unknown"
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
