import csv
from re import search
from typing import Dict, List

from .util import create_page, page_exists, run_template_modifier, database_update
from mwcleric import TemplateModifierBase
from mwparserfromhell.nodes import Template

prefix = "Upgrade/"

upgrade_template = """{{{{Upgrade Infobox
|Name={}
|Description={}
|Affects={}
|Target={}
|Levels={}
|Effects={}
|Credit Costs={}
|Resource Costs={}
}}}}
"""

upgrade_unlock_template = """{{{{Upgrade Infobox/Unlock
|Name={}
|Description={}
|Target={}
|Credits={}
|Resources={}
}}}}
"""

pages_to_update = {
    "regular": [],
    "enable": [],
}
data_to_update = {}


def full_page(sub_page: str) -> str:
    return prefix + sub_page


def upgrade_target(name: str) -> str:
    return "Shuttle" if name.split(' ')[0] == "Shuttle" else "Freighter"


def get_resources(entry: Dict[str, str], lvl: int) -> str:
    resources = []
    res = 1
    while entry.get(f"Lvl {lvl} Resource {res} Amount", "") != "":
        resources.append(f"{entry[f'Lvl {lvl} Resource {res} Name']}:{entry[f'Lvl {lvl} Resource {res} Amount']}")
        res += 1
    return ','.join(resources)


def get_steps(entry: Dict[str, str]) -> List[Dict[str, str]]:
    ret = [
        {
            "level": "0",
            "effect": entry["Lvl 0 Effect"],
            "credits": "",
            "resources": ""
        }
    ]

    # for every defined and currently available level
    lvl = 1
    while entry.get(f"Lvl {lvl} Cost Equivalent", "0") != "0":
        ret.append({
            "level": f"{lvl}",
            "credits": entry[f"Lvl {lvl} Credits"]
        })

        # Check effect for unlocks
        effect = entry[f"Lvl {lvl} Effect"].split('\n')
        if len(effect) == 1:
            ret[lvl]["effect"] = effect[0]
        else:
            lines = [effect[0]]
            i = 1
            while len(effect) > i:
                unlock = search(r"^Unlock (?P<cat>\w+) - (?P<name>[\w\s]+)$", effect[i])
                lines.append(f"Unlocks {{{{{unlock.group('cat')} icon|{unlock.group('name')}}}}}")
                i += 1
            ret[lvl]["effect"] = '<br />'.join(lines)

        # get the required resources
        ret[lvl]["resources"] = get_resources(entry, lvl)
        lvl += 1

    return ret


def make_upgrade_page(title: str, entry: Dict[str, str]) -> None:
    steps = get_steps(entry)
    create_page(title, upgrade_template.format(
        entry["Name"],
        entry["Description"],
        entry["Affects"],
        upgrade_target(entry["Name"]),
        ",".join([s["level"] for s in steps]),
        ";;".join([s["effect"] for s in steps]),
        ";;".join([s["credits"] for s in steps]),
        ";;".join([s["resources"] for s in steps])
    ))


def make_upgrade_enable_page(title: str, entry: Dict[str, str]) -> None:
    create_page(title, upgrade_unlock_template.format(
        entry["Name"],
        entry["Description"],
        upgrade_target(entry["Name"]),
        entry["Lvl 1 Credits"],
        get_resources(entry, 1)
    ))


class UpgradeModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Upgrade Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"])
        template.add("Description", info["Description"])
        template.add("Affects", info["Affects"])
        template.add("Target", upgrade_target(info["Name"]))

        steps = get_steps(info)
        template.add("Levels", ",".join([s["level"] for s in steps]))
        template.add("Effects", ";;".join([s["effect"] for s in steps]))
        template.add("Credit Costs", ";;".join([s["credits"] for s in steps]))
        template.add("Resource Costs", ";;".join([s["resources"] for s in steps]))


class UpgradeEnableModifier(TemplateModifierBase):
    def __init__(self, site, template, new_data, **data):
        self.new_data = new_data

        super().__init__(site, template, **data)

    def update_template(self, template: Template):
        if self.current_page.namespace != 0:
            # don't do anything outside the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return

        print("Updating Enable Upgrade Infobox on " + self.current_page.page_title)
        info = self.new_data[self.current_page.page_title]
        template.add("Name", info["Name"])
        template.add("Description", info["Description"])
        template.add("Target", upgrade_target(info["Name"]))
        template.add("Credits", info["Lvl 1 Credits"])
        template.add("Resources", get_resources(info, 1))


def run():
    with open("data files/Freighter_Shuttle Upgrades.csv") as f:
        upgrade_data = {}
        for row in csv.DictReader(f):
            page = full_page(row["Name"])
            upgrade_data[page] = row

    for page, data in upgrade_data.items():
        if data["Affects"] == "Unlock":
            if page_exists(page):
                pages_to_update["enable"].append(page)
                data_to_update[page] = data
            else:
                make_upgrade_enable_page(page, data)
        else:
            if page_exists(page):
                pages_to_update["regular"].append(page)
                data_to_update[page] = data
            else:
                make_upgrade_page(page, data)

    if len(pages_to_update["regular"]) > 0:
        run_template_modifier(
            UpgradeModifier,
            "Upgrade Infobox",
            pages_to_update["regular"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )

    if len(pages_to_update["enable"]) > 0:
        run_template_modifier(
            UpgradeEnableModifier,
            "Upgrade Infobox/Unlock",
            pages_to_update["enable"],
            "Automatic update from new data, "
            "see [https://github.com/alikimoko/astronomics-wiki-updater] for update script",
            new_data=data_to_update
        )


def force_database_update():
    with open("data files/Freighter_Shuttle Upgrades.csv") as f:
        for row in csv.DictReader(f):
            database_update(full_page(row["Name"]))


__all__ = ["run", "force_database_update"]
