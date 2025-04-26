import csv
from typing import Tuple

from.util import create_page, page_exists, run_template_modifier, database_update
from mwcleric import TemplateModifierBase
from mwparserfromhell.nodes import Template

prefix = "Resource/"

generic_template = """{{{{Resource Infobox
|Name={}
|Abbreviation={}
|Gameplay Type={}
|Credit Value Class={}
|Cash Value={}
|Value Modifier={}
}}}}"""

gem_template = """{{{{Resource Infobox/Gem
|Name={}
|Abbreviation={}
|Cash Value={}
}}}}"""

manufactured_template = """{{{{Resource Infobox/Manufactured
|Name={}
|Abbreviation={}
|Credit Value Class={}
|Cash Value={}
|Value Modifier={}
}}}}
"""

salvage_template = """{{{{Resource Infobox/Salvage
|Name={}
|Equipment Name={}
|Equipment Type={}
}}}}
The remains of a destroyed [[{}/{}|{}]]. You can collect it and repair it at the station for a reduced cost.
"""

pages_to_update = {
    "generic": [],
    "gem": [],
    "manufacture": [],
    "salvage": [],
}

data_to_update = {}


class GenericResourceModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Resource Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"])
        template.add("Abbreviation", info["Abbreviation"])
        template.add("Gameplay Type", info["Gameplay Type"])
        template.add("Credit Value Class", info["Credit Value Class"])
        template.add("Cash Value", info["$ Value"])


class GemResourceModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Gem Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"][:info["Name"].index("(") - 1])
        template.add("Abbreviation", info["Abbreviation"])
        template.add("Cash Value", info["$ Value"])


class ManufacturedResourceModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Manufactured Resource Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"])
        template.add("Abbreviation", info["Abbreviation"])
        template.add("Credit Value Class", info["Credit Value Class"])
        template.add("Cash Value", info["$ Value"])


class SalvageModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Salvage Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"])
        base_equipment, base_type = salvage_base_equipment(info["Name"])
        template.add("Equipment Name", base_equipment)
        template.add("Equipment Type", base_type)


def full_page(sub_page: str) -> str:
    return prefix + sub_page


def run():
    with open("data files/Resources.csv") as f:
        raw_resource_data = [row for row in csv.DictReader(f) if row["Name"] != "" and row["Name"] != "-"]

    # Column headers: Name, Abbreviation, Credit Value Class, Gameplay Type, $ Value, Credit Value, Found at
    # Split into resource categories

    for row in raw_resource_data:
        if row["Gameplay Type"] == "Salvage":
            salvage_resource(row)
        elif row["Gameplay Type"] == "Gem":
            gem_resource(row)
        elif row["Gameplay Type"] == "Manufactured":
            manufactured_resource(row)
        elif row["Gameplay Type"] == "Unknown"\
                or row["Gameplay Type"] == "Remains"\
                or row["Gameplay Type"] == ""\
                or row["Found at"] == "Upcoming":
            # Ignore Unknown (future content), Remains (handled by Gem), upcoming content and end of valid data
            pass
        else:
            generic_resource(row)

    if len(pages_to_update["generic"]) > 0:
        run_template_modifier(
            GenericResourceModifier,
            "Resource Infobox",
            pages_to_update["generic"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )
    if len(pages_to_update["gem"]) > 0:
        run_template_modifier(
            GemResourceModifier,
            "Resource Infobox/Gem",
            pages_to_update["gem"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )
    if len(pages_to_update["manufacture"]) > 0:
        run_template_modifier(
            ManufacturedResourceModifier,
            "Resource Infobox/Manufactured",
            pages_to_update["manufacture"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )
    if len(pages_to_update["salvage"]) > 0:
        run_template_modifier(
            SalvageModifier,
            "Resource Infobox/Salvage",
            pages_to_update["salvage"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )


def force_database_update():
    with open("data files/Resources.csv") as f:
        for row in csv.DictReader(f):
            # Filter empty rows
            if row["Name"] != "" and row["Name"] != "-":
                # Filter future content
                if row["Gameplay Type"] == "Unknown" \
                        or row["Gameplay Type"] == "Remains" \
                        or row["Gameplay Type"] == "" \
                        or row["Found at"] == "Upcoming":
                    continue
                if row["Gameplay Type"] == "Gem":
                    database_update(full_page(row["Name"][:row["Name"].index("(") - 1]))
                else:
                    database_update(full_page(row["Name"]))


def generic_resource(data: dict):
    page = full_page(data["Name"])
    if page_exists(page):
        # Update existing page
        pages_to_update["generic"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        WIKITEXT = generic_template.format(
            data["Name"],
            data["Abbreviation"],
            data["Gameplay Type"],
            data["Credit Value Class"],
            data["$ Value"],
            ""
        )
        WIKITEXT += "\n{} can be found on {}".format(
            data["Name"],
            ", ".join(["[[Asteroid/{}|{}]]".format(s, s) for s in data["Found at"].split(", ")])
        )

        create_page(page, WIKITEXT)


def gem_resource(data: dict):
    gem_name = data["Name"][:data["Name"].index("(") - 1]
    page = full_page(gem_name)
    if page_exists(page):
        # Update existing page
        pages_to_update["gem"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        WIKITEXT = gem_template.format(
            gem_name,
            data["Abbreviation"],
            data["$ Value"]
        )
        WIKITEXT += "\n{} can be found on {}".format(
            gem_name,
            ", ".join(["[[Asteroid/{}|{}]]".format(s, s) for s in data["Found at"].split(", ")])
        )

        create_page(page, WIKITEXT)


def manufactured_resource(data: dict):
    page = full_page(data["Name"])
    if page_exists(page):
        # Update existing page
        pages_to_update["manufacture"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        WIKITEXT = manufactured_template.format(
            data["Name"],
            data["Abbreviation"],
            data["Credit Value Class"],
            data["$ Value"],
            ""
        )

        create_page(page, WIKITEXT)


def salvage_resource(data: dict):
    page = full_page(data["Name"])
    if page_exists(page):
        # Update existing page
        pages_to_update["salvage"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        base_equipment, equipment_type = salvage_base_equipment(data["Name"])
        create_page(page, salvage_template.format(
            data["Name"],
            base_equipment,
            equipment_type,
            equipment_type,
            base_equipment,
            base_equipment,
        ))


def salvage_base_equipment(name: str) -> Tuple[str, str]:
    base_name = name[:name.index("(") - 1]
    with open("data files/Equipment and blueprints.csv") as f:
        for row in csv.DictReader(f):
            if base_name in row["Name"] and row["Type"] in ["Bot", "Deployable"]:
                return row["Name"], row["Type"]
    return base_name, "Equipment"


__all__ = ["run", "force_database_update"]
