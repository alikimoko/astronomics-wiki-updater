from .util import set_client
from .asteroids import run as asteroid_updater, force_database_update as force_asteroid_update
from .equipment import run as equipment_updater, force_database_update as force_equipment_update
from .resources import run as resource_updater, force_database_update as force_resource_update
from .stations import run as station_updater, force_database_update as force_station_update
from .upgrades import run as upgrade_updater, force_database_update as force_upgrade_update

# Run all update scripts in
updaters_to_run = [
    # Page data update scripts
    #asteroid_updater,
    #equipment_updater,
    #resource_updater,
    #station_updater,
    #upgrade_updater,

    # Database update checkers
    force_asteroid_update,
    force_equipment_update,
    force_resource_update,
    force_station_update,
    force_upgrade_update,
]


def run_all():
    """
    Run all updaters that need to run.
    If updaters are unnecessary or outdated, change here wetter they run or not.
    """
    for updater in updaters_to_run:
        updater()

