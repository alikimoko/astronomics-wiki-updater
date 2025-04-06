import csv
from.util import create_page, page_exists, run_template_modifier
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

gem_template = """{{{{Gem Infobox
|Name={}
|Abbreviation={}
|Cash Value={}
}}}}"""

manufactured_template = """{{{{Manufactured Resource Infobox
|Name={}
|Abbreviation={}
|Credit Value Class={}
|Cash Value={}
|Value Modifier={}
}}}}
"""

pages_to_update = {
    "generic": [],
    "gem": [],
    "manufacture": []
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

        info = self.new_data[self.current_page.page_title]
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

        info = self.new_data[self.current_page.page_title]
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

        info = self.new_data[self.current_page.page_title]
        template.add("Abbreviation", info["Abbreviation"])
        template.add("Credit Value Class", info["Credit Value Class"])
        template.add("Cash Value", info["$ Value"])


def full_page(sub_page: str) -> str:
    return prefix + sub_page


def run():
    with open("data files/Resources.csv") as f:
        raw_resource_data = [row for row in csv.DictReader(f)]

    # Column headers: Name, Abbreviation, Credit Value Class, Gameplay Type, $ Value, Credit Value, Found at
    # Split into resource categories

    for row in raw_resource_data:
        if row["Gameplay Type"] == "Salvage":
            salvage_resource(row)
        elif row["Gameplay Type"] == "Gem":
            gem_resource(row)
        elif row["Gameplay Type"] == "Manufactured":
            manufactured_resource(row)
        elif row["Gameplay Type"] == "Unknown" or row["Gameplay Type"] == "Remains" or row["Gameplay Type"] == "":
            # Ignore Unknown (future content), Remains (handled by Gem) and end of valid data
            pass
        else:
            generic_resource(row)

    if len(pages_to_update["generic"]) > 0:
        run_template_modifier(
            GenericResourceModifier,
            "Resource Infobox",
            pages_to_update["generic"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )
    if len(pages_to_update["gem"]) > 0:
        run_template_modifier(
            GemResourceModifier,
            "Gem Infobox",
            pages_to_update["gem"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )
    if len(pages_to_update["manufacture"]) > 0:
        run_template_modifier(
            GenericResourceModifier,
            "Manufactured Resource Infobox",
            pages_to_update["manufacture"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )


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
        WIKITEXT += "{} can be found on {}".format(
            data["Name"],
            ", ".join(["[[Asteroid/{}|{}]]".format(s, s) for s in data["Found at"].split(", ")])
        )

        create_page(page, WIKITEXT)


def gem_resource(data: dict):
    gem_name = data["Name"].split()[0]
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
        WIKITEXT += "{} can be found on {}".format(
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
        pages_to_update["generic"].append(page)
        data_to_update[page] = data
    else:
        # Create new page
        WIKITEXT = generic_template.format(
            data["Name"],
            data["Abbreviation"],
            "Salvage",
            data["Credit Value Class"],
            data["$ Value"],
            ""
        )
        base_equipment = data["Name"].split()[0]
        WIKITEXT += "The remains of a destroyed [[Equipment/{}|{}]]. " \
                    "You can collect it and repair it at the station for a reduced cost.\n" \
                    "[[Category:Salvage]]"\
            .format(base_equipment, base_equipment)

        create_page(page, WIKITEXT)


__all__ = ["run"]
