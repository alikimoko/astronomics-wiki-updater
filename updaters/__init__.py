from .util import set_client
from .resources import run as resource_updater

# Run all update scripts in
updaters_to_run = [
    resource_updater
]


def run_all():
    """
    Run all updaters that need to run.
    If updaters are unnecessary or outdated, change here wetter they run or not.
    """
    for updater in updaters_to_run:
        updater()

