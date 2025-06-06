import csv
from typing import Tuple

from .util import create_page, page_exists, run_template_modifier, database_update
from mwcleric import TemplateModifierBase
from mwparserfromhell.nodes import Template

prefix = "Resource/"

pages_to_update = {
    "generic": [],
    "gem": [],
    "liquid": [],
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


class LiquidResourceModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Liquid Resource Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"])
        template.add("Abbreviation", info["Abbreviation"])
        template.add("Credit Value Class", info["Credit Value Class"])
        template.add("Cash Value", info["$ Value"])
        template.add("Special Property", info["Special Effect"])


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
        template.add("Repair Cost", info["Repair Cost"])


def full_page(sub_page: str) -> str:
    if "(Salvage)" in sub_page:
        return "Salvage/" + sub_page[:sub_page.index("(") - 1]
    return prefix + sub_page


def run():
    with open("data files/Resources.csv") as f:
        raw_resource_data = [row for row in csv.DictReader(f) if row["Name"] != "" and row["Name"] != "-"]

    # Column headers:
    # Name
    # Abbreviation
    # Credit Value Class
    # Gameplay Type
    # $ Value
    # Credit Value
    # Repair Cost
    # Special Effect
    # Found at

    # Split into resource categories
    for row in raw_resource_data:
        if row["Gameplay Type"] == "Salvage":
            salvage_resource(row)
        elif row["Gameplay Type"] == "Gem":
            gem_resource(row)
        elif row["Gameplay Type"] == "Liquid":
            liquid_resource(row)
        elif row["Gameplay Type"] == "Manufactured":
            manufactured_resource(row)
        elif row["Gameplay Type"] == "Unknown" \
                or row["Gameplay Type"] == "Remains" \
                or row["Gameplay Type"] == "" \
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
    if len(pages_to_update["liquid"]) > 0:
        run_template_modifier(
            LiquidResourceModifier,
            "Resource Infobox/Liquid",
            pages_to_update["liquid"],
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
        create_page(page, f"""{{{{Beta content}}}}
{{{{Resource Infobox
|Name={data["Name"]}
|Abbreviation={data["Abbreviation"]}
|Gameplay Type={data["Gameplay Type"]}
|Credit Value Class={data["Credit Value Class"]}
|Cash Value={data["$ Value"]}
|Value Modifier=
}}}}

{data["Name"]} can be found on {", ".join([f"{{{{Asteroid icon|{s}}}}}" for s in data["Found at"].split(", ")])}

{{{{Main site nav}}}}
""")


def gem_resource(data: dict):
    gem_name = data["Name"][:data["Name"].index("(") - 1]
    page = full_page(gem_name)
    if page_exists(page):
        # Update existing page
        pages_to_update["gem"].append(page)
        data_to_update[page] = data
    else:
        # Create new page

        create_page(page, f"""{{{{Beta content}}}}
{{{{Resource Infobox/Gem
|Name={gem_name}
|Abbreviation={data["Abbreviation"]}
|Cash Value={data["$ Value"]}

{gem_name} can be found on {", ".join([f"{{{{Asteroid icon|{s}}}}}" for s in data["Found at"].split(", ")])}

{{{{Main site nav}}}}
}}}}""")


def liquid_resource(data: dict):
    page = full_page(data["Name"])
    if page_exists(page):
        # Update existing page
        pages_to_update["liquid"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        create_page(page, f"""{{{{Beta content}}}}
{{{{Resource Infobox/Liquid
|Name={data["Name"]}
|Abbreviation={data["Abbreviation"]}
|Credit Value Class={data["Credit Value Class"]}
|Cash Value={data["$ Value"]}
|Value Modifier=
|Special Property={data["Special Effect"]}
}}}}

{data["Name"]} can be found on {", ".join([f"{{{{Asteroid icon|{s}}}}}" for s in data["Found at"].split(", ")])}

{{{{Main site nav}}}}
""")


def manufactured_resource(data: dict):
    page = full_page(data["Name"])
    if page_exists(page):
        # Update existing page
        pages_to_update["manufacture"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        create_page(page, f"""{{{{Beta content}}}}
{{{{Resource Infobox/Manufactured
|Name={data["Name"]}
|Abbreviation={data["Abbreviation"]}
|Credit Value Class={data["Credit Value Class"]}
|Cash Value={data["$ Value"]}
|Value Modifier=
}}}}

{{{{Main site nav}}}}
""")


def salvage_resource(data: dict):
    page = full_page(data["Name"])
    if page_exists(page):
        # Update existing page
        pages_to_update["salvage"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        base_equipment, equipment_type = salvage_base_equipment(data["Name"])
        create_page(page, f"""{{{{Beta content}}}}
{{{{Salvage Infobox
|Name={data["Name"]}
|Equipment Name={base_equipment}
|Equipment Type={equipment_type}
|Repair Cost={data["Repair Cost"]}
}}}}

The remains of a destroyed {{{{{equipment_type} icon|{base_equipment}}}}}. You can collect it and repair it at the station for a reduced cost.

{{{{Main site nav}}}}
""")


def salvage_base_equipment(name: str) -> Tuple[str, str]:
    base_name = name[:name.index("(") - 1]
    with open("data files/Equipment and blueprints.csv") as f:
        for row in csv.DictReader(f):
            if base_name in row["Name"] and row["Type"] in ["Bot", "Deployable"]:
                return row["Name"], row["Type"]
    return base_name, "Equipment"


__all__ = ["run", "force_database_update"]
