import csv
from typing import List

from.util import create_page, page_exists, run_template_modifier, database_update
from mwcleric import TemplateModifierBase
from mwparserfromhell.nodes import Template

prefix = "Station/"

pages_to_update = []
data_to_update = {}


def full_page(sub_page: str) -> str:
    return prefix + sub_page


def construct_contract_list(contracts: List[dict]) -> str:
    # Table headers:
    # Station
    # Internal ID
    # Title
    # Required Quantity
    # Reward
    # Notes
    wiki_text = []
    for i in range(len(contracts)):
        contract = contracts[i]
        wiki_text.append(f"""{{{{Station Infobox/Contract
  |Station={contract["Station"]}
  |Contract Number={i + 1}
  |Title={contract["Title"]}
  |Internal ID={contract["Internal ID"]}
  |Requirements={contract["Required Quantity"]}
  |Reward={contract["Reward"]}
  |Notes={contract["Notes"]}
}}}}""")

    return "".join(wiki_text)


def make_station_page(page: str, data: dict) -> None:
    # Table headers:
    # Name
    # Depth (kkm)
    # Contracts
    # Max Reputation
    create_page(page, f"""{{{{Stub}}}}
{{{{Beta content}}}}
{{{{Station Infobox
|Station={data["Name"]}
|Depth={data["Depth (kkm)"]}
|Refuel Cost={data["Refuel Cost"]}
|Contracts={construct_contract_list(data["Contracts"])}
}}}}

== Asteroids ==
{{{{Asteroid table|Region|{data["Name"]}}}}}

== Contracts ==
{{{{For|a full list of contracts|Contracts}}}}
{{{{Contracts table|{data["Name"]}}}}}

== Unlocked equipment ==
{{{{Station unlocks table|{data["Name"]}}}}}

== Available upgrades ==
The following new upgrades can be unlocked using the resources you can find in this region:

{{{{Main site nav}}}}
""")


class StationModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Station Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"])
        template.add("Depth", info["Depth (kkm)"])
        template.add("Refuel Cost", info["Refuel Cost"])
        template.add("Contracts", construct_contract_list(info["Contracts"]))


def run():
    with open("data files/Stations.csv") as f:
        # Load all stations
        station_data = {}
        for row in csv.DictReader(f):
            page = full_page(row["Name"])
            station_data[page] = row
            station_data[page]["Contracts"] = []

    with open("data files/Contracts.csv") as f:
        # Load all contracts and link them to their stations
        for row in csv.DictReader(f):
            station_data[full_page(row["Station"])]["Contracts"].append(row)

    for page, data in station_data.items():
        if data["Depth (kkm)"] == "":
            # Filter not yet released stations
            continue
        if page_exists(page):
            pages_to_update.append(page)
            data_to_update[page] = data
        else:
            make_station_page(page, data)

    if len(pages_to_update) > 0:
        run_template_modifier(
            StationModifier,
            "Station Infobox",
            pages_to_update,
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )


def force_database_update():
    with open("data files/Stations.csv") as f:
        for row in csv.DictReader(f):
            # Filter empty rows
            if row["Depth (kkm)"] != "":
                database_update(full_page(row["Name"]))


__all__ = ["run", "force_database_update"]
