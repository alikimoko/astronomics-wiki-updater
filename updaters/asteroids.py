import csv
from typing import List

from .util import create_page, page_exists, run_template_modifier, database_update
from mwcleric import TemplateModifierBase
from mwparserfromhell.nodes import Template

prefix = "Asteroid/"

pages_to_update = []
data_to_update = {}


def full_page(sub_page: str) -> str:
    return prefix + sub_page


def parse_resources(field: str) -> List[str]:
    if field == "" or field == "-":
        return []
    return sorted([r for r in field.split(", ")], key=str.casefold)


def make_asteroid_page(page: str, data: dict) -> None:
    # Table headers:
    # Internal id
    # In-Game ID
    # Composition
    # Region
    # Pirate warning
    # Surface resource
    # Underground deposit (Common)
    # Underground deposit (Rare)
    # Liquids
    # Gasses
    create_page(page, f"""{{{{Beta content}}}}
{{{{Asteroid Infobox
|Name={data["In-Game ID"]}
|Region={data["Region"]}
|Composition={data["Composition"]}
|Pirates={data["Pirate warning"]}
|Surface Resources={",".join(parse_resources(data["Surface resource"]))}
|Deposit Resources={",".join(sorted(parse_resources(data["Underground deposit (Common)"])
                                    + parse_resources(data["Underground deposit (Rare)"]),
                                    key=str.casefold))}
|Liquid Resources={",".join(parse_resources(data["Liquids"]))}
|Gas Resources={",".join(parse_resources(data["Gasses"]))}
}}}}

{{{{Main site nav}}}}
""")


class AsteroidModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Asteroid Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["In-Game ID"])
        template.add("Region", info["Region"])
        template.add("Composition", info["Composition"])
        template.add("Pirates", info["Pirate warning"])
        template.add("Surface Resources", ",".join(parse_resources(info["Surface resource"])))
        template.add("Deposit Resources", ",".join(sorted(parse_resources(info["Underground deposit (Common)"])
                                                          + parse_resources(info["Underground deposit (Rare)"]),
                                                          key=str.casefold)))
        template.add("Liquid Resources", ",".join(parse_resources(info["Liquids"])))
        template.add("Gas Resources", ",".join(parse_resources(info["Gasses"])))


def run():
    with open("data files/Asteroid resources.csv") as f:
        asteroid_data = {}
        for row in csv.DictReader(f):
            if row["In-Game ID"] == "" or row["Internal id"] == "" or row["Composition"] == "Station":
                continue
            page = full_page(row["In-Game ID"])
            asteroid_data[page] = row

    for page, data in asteroid_data.items():
        if page_exists(page):
            pages_to_update.append(page)
            data_to_update[page] = data
        else:
            make_asteroid_page(page, data)

    if len(pages_to_update) > 0:
        run_template_modifier(
            AsteroidModifier,
            "Asteroid Infobox",
            pages_to_update,
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )


def force_database_update():
    with open("data files/Asteroid resources.csv") as f:
        for row in csv.DictReader(f):
            # Filter empty rows
            if row["In-Game ID"] != "" and row["Composition"] != "Station":
                database_update(full_page(row["In-Game ID"]))


__all__ = ["run", "force_database_update"]
