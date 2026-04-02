import os, sys
from datetime import datetime
import shutil
from util.configuration import Configuration
import time
from pathlib import Path

def create_experiment_folder() -> str:
    """
    Creates a new experiment folder with current datetime.
    Copies configuration.py and experiment file (from config) as used_* files.
    Returns the relative path to the created experiment folder.
    """
    ROOT_DIR = Path(__file__).resolve().parents[3]
    base_dir = ROOT_DIR / "src" / "exp2" / "stats_data"
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_folder = base_dir / f"experiment{now_str}"
    experiment_folder.mkdir(parents=True, exist_ok=True)

    # Copy configuration.py and experiment file as used_* files
    config_src = ROOT_DIR / "src" / "exp2" / "util" / "configuration.py"
    config_dst = experiment_folder / "used_configuration.py"
    shutil.copyfile(config_src, config_dst)

    return str(experiment_folder)

def create_testcase_folder(experiment_folder_name: str) -> str:
    """
    Creates a new testcase folder with current datetime inside the given experiment folder.
    Returns the path to the created testcase folder.
    """

    ROOT_DIR = Path(__file__).resolve().parents[3]

    base_dir = ROOT_DIR / "src" / "exp2" / "stats_data"

    experiment_folder = base_dir / experiment_folder_name

    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    testcase_folder = experiment_folder / f"testcase{now_str}"

    testcase_folder.mkdir(parents=True, exist_ok=True)

    # Copy experiment file (portable)
    if hasattr(Configuration, "exp_full_path"):

        experiment_src = Path(Configuration.exp_full_path)

        if experiment_src.exists():

            experiment_dst = testcase_folder / f"used_{experiment_src.name}"

            shutil.copyfile(experiment_src, experiment_dst)

    return str(testcase_folder)