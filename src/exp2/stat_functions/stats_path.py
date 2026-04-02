from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).resolve().parents[3]

# Root stats_data directory
base_root = ROOT_DIR / "src" / "exp2" / "stats_data"


def get_latest_experiment_folder() -> str or None:
    """
    Returns the most recently created experiment folder inside stats_data,
    or None if no experiment folder exists.
    """

    if not base_root.exists():
        return None

    folders = [
        f.name
        for f in base_root.iterdir()
        if f.is_dir() and f.name.startswith("experiment")
    ]

    if not folders:
        return None

    # Sort by folder name (timestamp format ensures correct ordering)
    folders.sort(reverse=True)

    return folders[0]


# Set experiment_folder to latest or None
experiment_folder = get_latest_experiment_folder()

# Default stats folder
stats_folder = experiment_folder