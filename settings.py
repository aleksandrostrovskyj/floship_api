import pathlib
import yaml

BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR / 'config' / 'floship.yaml'


def get_config(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


config = get_config(config_path)