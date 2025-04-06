from typing import List, Optional, Type
from mwcleric import TemplateModifierBase, WikiggClient

WIKI_CLIENT: Optional[WikiggClient] = None


def set_client(client: WikiggClient):
    global WIKI_CLIENT
    WIKI_CLIENT = client


def run_template_modifier(modifier: Type[TemplateModifierBase], template: str, pages: List[str], summary: str, **extra):
    modifier(WIKI_CLIENT, template, title_list=pages, summary=summary, **extra).run()


def page_exists(page: str) -> bool:
    return WIKI_CLIENT.client.pages.get(page).exists


def create_page(page: str, content: str):
    print("Creating page: " + page)
    WIKI_CLIENT.save_title(
        page,
        content,
        summary="Automated page creation, "
                "see [https://github.com/alikimoko/astronomics-wiki-updater astronomics-wiki-updater] for update script"
    )


