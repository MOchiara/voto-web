import xarray as xr
from pathlib import Path
import logging
import os
import json
from voto.data.db_session import initialise_database
from voto.services.mission_service import add_glidermission
from voto.services.platform_service import update_glider

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
_log = logging.getLogger(__name__)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)


def add_nrt_profiles():
    in_dir = Path("/home/callum/Documents/data-flow/nrt_data")
    _log.info(f"adding nrt profiles from {in_dir}")
    ncs = list(in_dir.rglob("*gridfiles/*.nc"))
    _log.info(f"found {len(ncs)} files")
    for file in ncs:
        rawncs = list(Path("/".join(file.parts[:-2]) + "/rawnc").glob("*.nc"))
        dive_nums = []
        for dive in rawncs:
            try:
                dive_nums.append(int(dive.name.split(".")[-2]))
            except ValueError:
                continue
        max_profile = 2 * max(dive_nums)
        ds = xr.open_dataset(file)
        mission = add_glidermission(ds, total_profiles=max_profile)
        update_glider(mission)
    _log.info("added all nrt profiles")


def add_complete_profiles():
    full_dir = Path(
        "/home/callum/Documents/data-flow/comlete_data/data/data_l0_pyglider/complete_mission"
    )
    full_ncs = list(full_dir.rglob("*gridfiles/*.nc"))
    for file in full_ncs:
        ds = xr.open_dataset(file)
        mission = add_glidermission(ds, mission_complete=True)
        update_glider(mission)


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{folder}/voto_add_data.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    initialise_database(
        user=secrets["mongo_user"],
        password=secrets["mongo_password"],
        port=int(secrets["mongo_port"]),
        server=secrets["mongo_server"],
    )
    add_nrt_profiles()
