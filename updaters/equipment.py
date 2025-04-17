import csv
from typing import Dict, List, Union

from .util import create_page, page_exists, run_template_modifier, database_update
from mwcleric import TemplateModifierBase
from mwparserfromhell.nodes import Template

simple_template = """{{{{Equipment Infobox
|Name={}
|Category={}
|Station={}
|{}={}
|Short Description={}
|In Game Description={}
}}}}
{}
It can be purchased at the {} console in the {} tab
"""

structure_template = """{{{{Equipment Infobox/Structure
|Name={}
|Station={}
|{}={}
|Build Cost={}
|Short Description={}
|In Game Description={}
}}}}
{}
It can be purchased at the {} console in the {} tab
"""

tool_template = """{{{{Equipment Infobox/Tool
|Name={}
|tabs={}
|Stations={}
|Special Unlocks={}
|Prices={}
|Short Descriptions={}
|In Game Descriptions={}
}}}}
{}
It can be purchased at the {} console in the {} tab
"""

modification_template = """{{{{Equipment Infobox/Modification
|Name={}
|Station={}
|Price={}
|Short Description={}
|In Game Description={}
}}}}
{}
It can be purchased at the {} console in the {} tab
"""

manufacturing_template = """{{{{Equipment Infobox/Manufacturing
|Name={}
|Station={}
|{}={}
|Short Description={}
|In Game Description={}
|Recipes={}
}}}}
{}
It can be purchased at the {} console in the {} tab
"""

manufacturing_recipe_template = """{{{{Equipment Infobox/Manufacturing/Recipe
|Recipe ID={}
|Machine={}
|Processing Time={}
|Ingredients={}
|Products={}
}}}}"""

pages_to_update = {
    "simple": [],
    "structure": [],
    "leveled tool": [],
    "modification": [],
    "machine": [],
}
data_to_update = {}


def construct_page_title(entry: Dict[str, str]) -> str:
    if entry["Type"] == "Tool" and entry["Variant"]:
        return "Tool/" + entry["Group"]
    if entry["Type"] == "Modification":
        # Change this when modifications get variants
        return "Modification/" + entry["Group"]

    return entry["Type"] + "/" + entry["Name"]


def make_simple_page(title: str, entry: Dict[str, str]) -> None:
    args = [entry["Name"], entry["Type"], entry["Station Unlocked"]]\
           + (["Special Unlock", entry["Special Unlock"]] if entry["Special Unlock"] else ["Price", entry["Price"]])\
           + [entry["Short Description"], entry["In Game Description"], entry["Description"],
              entry["Console"], entry["Tab"]]
    create_page(title, simple_template.format(*args))


def make_structure_page(title: str, entry: Dict[str, str]) -> None:
    args = [entry["Name"], entry["Station Unlocked"]]\
           + (["Special Unlock", entry["Special Unlock"]] if entry["Special Unlock"] else ["Price", entry["Price"]])\
           + [entry["Build Cost"], entry["Short Description"], entry["In Game Description"], entry["Description"],
              entry["Console"], entry["Tab"]]
    create_page(title, structure_template.format(*args))


def make_tool_page(title: str, entries: List[Dict[str, str]]) -> None:
    args: List[str] = [
        entries[0]['Group'],
        ','.join([entry['Variant'] for entry in entries]),
        ';;'.join([entry['Station Unlocked'] for entry in entries]),
        ';;'.join([entry['Special Unlock'] for entry in entries]),
        ';;'.join([entry['Price'] for entry in entries]),
        ';;'.join([entry['Short Description'] for entry in entries]),
        ';;'.join([entry['In Game Description'] for entry in entries]),
        '<br />'.join([entry['Variant'] + ': ' + entry['Description'] for entry in entries]),
        entries[0]['Console'],
        entries[0]['Tab']
    ]
    create_page(title, tool_template.format(*args))


def make_modification_page(title: str, entries: List[Dict[str, str]]) -> None:
    # This should be changed when there are multiple modifications for the same group
    args = [
        entries[0]["Group"],
        entries[0]["Station Unlocked"],
        entries[0]["Price"],
        entries[0]["Short Description"],
        entries[0]["In Game Description"],
        entries[0]["Description"],
        entries[0]["Console"],
        entries[0]["Tab"]
    ]
    create_page(title, modification_template.format(*args))


def make_recipe(recipe: Dict[str, str]) -> str:
    args = [
        recipe["Identifier"],
        recipe["Machine"],
        recipe["Processing time"],
    ]

    ingredients = []
    i = 1
    while recipe.get(f"Input {i} Name", None):
        if recipe[f'Input {i} Name'] == '-':
            break
        ingredients.append(f"{recipe[f'Input {i} Name']}:{recipe[f'Input {i} Quantity']}")
        i += 1
    args.append(','.join(ingredients))

    products = []
    i = 1
    while recipe.get(f"Product {i} Name", None):
        if recipe[f'Product {i} Name'] == '-':
            break
        products.append(f"{recipe[f'Product {i} Name']}:{recipe[f'Product {i} Quantity']}")
        i += 1
    args.append(','.join(products))

    return manufacturing_recipe_template.format(*args)


def make_machine_page(title: str, entry: Dict[str, Union[str, List[Dict[str, str]]]]):
    args = [entry["Name"], entry["Station Unlocked"]] \
           + (["Special Unlock", entry["Special Unlock"]] if entry["Special Unlock"] else ["Price", entry["Price"]]) \
           + [
                entry["Short Description"],
                entry["In Game Description"],
                ';;'.join([make_recipe(r) for r in entry["Recipes"]]),
                entry["Description"],
                entry["Console"],
                entry["Tab"]
           ]
    create_page(title, manufacturing_template.format(*args))


class SimpleEquipmentModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Simple Equipment Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Category", info["Type"])
        template.add("Station", info["Station Unlocked"])
        if info["Special Unlock"]:
            if template.has("Price"):
                template.remove("Price")
            template.add("Special Unlock", info["Special Unlock"])
        else:
            if template.has("Special Unlock"):
                template.remove("Special Unlock")
            template.add("Price", info["Price"])
        template.add("Short Description", info["Short Description"])
        template.add("In Game Description", info["In Game Description"])


class StructureEquipmentModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Structure Equipment Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Station", info["Station Unlocked"])
        if info["Special Unlock"]:
            if template.has("Price"):
                template.remove("Price")
            template.add("Special Unlock", info["Special Unlock"])
        else:
            if template.has("Special Unlock"):
                template.remove("Special Unlock")
            template.add("Price", info["Price"])
        template.add("Build Cost", info["Build Cost"])
        template.add("Short Description", info["Short Description"])
        template.add("In Game Description", info["In Game Description"])


class ToolEquipmentModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Tool Equipment Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add('tabs', ','.join([entry['Variant'] for entry in info]))
        template.add('Stations', ';;'.join([entry['Station Unlocked'] for entry in info]))
        template.add('Special Unlocks', ';;'.join([entry['Special Unlock'] for entry in info]))
        template.add('Prices', ';;'.join([entry['Price'] for entry in info]))
        template.add('Short Descriptions', ';;'.join([entry['Short Description'] for entry in info]))
        template.add('In Game Descriptions', ';;'.join([entry['In Game Description'] for entry in info]))


class ModificationEquipmentModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        # change this when there are multiple pieces of equipment in a modification group
        print("Updating Modification Equipment Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Station", info[0]["Station Unlocked"])
        template.add("Price", info[0]["Price"])
        template.add("Short Description", info[0]["Short Description"])
        template.add("In Game Description", info[0]["In Game Description"])


class MachineEquipmentModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        # change this when there are multiple pieces of equipment in a modification group
        print("Updating Manufacturing Equipment Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Station", info["Station Unlocked"])
        if info["Special Unlock"]:
            if template.has("Price"):
                template.remove("Price")
            template.add("Special Unlock", info["Special Unlock"])
        else:
            if template.has("Special Unlock"):
                template.remove("Special Unlock")
            template.add("Price", info["Price"])
        template.add("Short Description", info["Short Description"])
        template.add("In Game Description", info["In Game Description"])
        template.add("Recipes", ';;'.join([make_recipe(r) for r in info["Recipes"]]))


def run():
    with open("data files/Equipment and blueprints.csv") as f:
        equipment_data = [row for row in csv.DictReader(f) if row["Name"] != ""]
    with open("data files/Manufacturing.csv") as f:
        recipe_data = [row for row in csv.DictReader(f) if row["Identifier"] != ""]

    pages = {
        "simple": {},
        "structure": {},
        "leveled tool": {},
        "modification": {},
        "machine": {},
    }

    # Preprocess data
    for entry in equipment_data:
        page = construct_page_title(entry)

        if entry["Type"] == "Tool" and entry["Name"].find(" Lvl") > -1:
            if page not in pages["leveled tool"]:
                pages["leveled tool"][page] = []
            pages["leveled tool"][page].append(entry)
        elif entry["Type"] == "Modification":
            # Change this if name specification changes with multiple variants
            if page not in pages["modification"]:
                pages["modification"][page] = []
            pages["modification"][page].append(entry)
        elif entry["Type"] == "Structure":
            pages["structure"][page] = entry
        elif entry["Type"] == "Manufacturing":
            pages["machine"][page] = entry
            pages["machine"][page]["Recipes"] = []
        else:
            pages["simple"][page] = entry

    for entry in recipe_data:
        page = "Manufacturing/" + entry["Machine"]
        pages["machine"][page]["Recipes"].append(entry)

    # Make now pages or mark for update
    for page, data in pages["simple"].items():
        if page_exists(page):
            pages_to_update["simple"].append(page)
            data_to_update[page] = data
        else:
            make_simple_page(page, data)

    for page, data in pages["structure"].items():
        if page_exists(page):
            pages_to_update["structure"].append(page)
            data_to_update[page] = data
        else:
            make_structure_page(page, data)

    for page, data in pages["leveled tool"].items():
        if page_exists(page):
            pages_to_update["leveled tool"].append(page)
            data_to_update[page] = data
        else:
            make_tool_page(page, data)

    for page, data in pages["modification"].items():
        if page_exists(page):
            pages_to_update["modification"].append(page)
            data_to_update[page] = data
        else:
            make_modification_page(page, data)

    for page, data in pages["machine"].items():
        if page_exists(page):
            pages_to_update["machine"].append(page)
            data_to_update[page] = data
        else:
            make_machine_page(page, data)

    modifier_class = {
        "simple": SimpleEquipmentModifier,
        "structure": StructureEquipmentModifier,
        "leveled tool": ToolEquipmentModifier,
        "modification": ModificationEquipmentModifier,
        "machine": MachineEquipmentModifier,
    }

    modifier_name = {
        "simple": "Equipment Infobox",
        "structure": "Equipment Infobox/Structure",
        "leveled tool": "Equipment Infobox/Tool",
        "modification": "Equipment Infobox/Modification",
        "machine": "Equipment Infobox/Manufacturing",
    }

    for group in pages_to_update.keys():
        if len(pages_to_update[group]) > 0:
            run_template_modifier(
                modifier_class[group],
                modifier_name[group],
                pages_to_update[group],
                "Automatic update from new data, "
                "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
                new_data=data_to_update
            )


def force_database_update():
    updated = []
    with open("data files/Equipment and blueprints.csv") as f:
        for row in csv.DictReader(f):
            # Filter empty rows
            if row["Name"] != "":
                title = construct_page_title(row)
                if title not in updated:
                    # Make sure variants don't cause multiple updates
                    database_update(title)
                    updated.append(title)


__all__ = ["run", "force_database_update"]
