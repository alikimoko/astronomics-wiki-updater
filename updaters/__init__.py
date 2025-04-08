from .util import set_client
from .resources import run as resource_updater, force_database_update as force_resource_update
from .stations import run as station_updater, force_database_update as force_station_update

# Run all update scripts in
updaters_to_run = [
    #resource_updater,
    #force_resource_update,
    #station_updater,
    force_station_update,
]


def run_all():
    """
    Run all updaters that need to run.
    If updaters are unnecessary or outdated, change here wetter they run or not.
    """
    for updater in updaters_to_run:
        updater()

