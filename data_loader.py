# =========================
# DATA LOADER
# =========================

import json
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(PROJECT_ROOT, "data")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# STATIC LOAD
# -------------------------
ASTEROID_DATA = load_json(os.path.join(BASE_PATH, "asteroids.json"))
RECIPE_DATA = load_json(os.path.join(BASE_PATH, "recipes.json"))


# -------------------------
# LOAD LOGS (dynamic)
# -------------------------
def load_logs():
    logs = {}
    folder = os.path.join(BASE_PATH, "logs")

    for file in os.listdir(folder):
        if file.endswith(".json"):
            path = os.path.join(folder, file)
            data = load_json(path)
            logs[data["id"]] = data

    return logs


# -------------------------
# HELPERS
# -------------------------
def get_asteroid_data(name):
    return ASTEROID_DATA.get(name, {})


def get_all_asteroid_types():
    return list(ASTEROID_DATA.keys())


def get_recipe(name):
    return RECIPE_DATA.get(name, {}).get("cost", {})


def get_all_recipes():
    return RECIPE_DATA
