import json
from pathlib import Path

CONFIG_PATH = Path("config.json")

def save_token(token):
    config = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    config["X-OBSERVATORY-AUTH"] = token
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def load_token():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            return config.get("X-OBSERVATORY-AUTH")
    return None
