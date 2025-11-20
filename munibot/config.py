import configparser
import os
import logging
import importlib
import inspect
from pathlib import Path

from importlib.metadata import entry_points

config = {}


def load_config(path):

    if not os.path.exists(path):
        raise ValueError(
            """
INI file not found. It must be a "munibot.ini" file in the current directory,
otherwise pass the location with the "--config" parameter""".strip()
        )

    cp = configparser.RawConfigParser()
    cp.read(path)
    for section in cp.sections():
        config[section] = dict(cp[section])


def load_profiles():
    from munibot.profiles.base import BaseProfile

    profiles = {}

    # Load profiles included in this package
    profiles_dir = Path(__file__).parent / "profiles"

    for profile_file in profiles_dir.glob("*.py"):
        if profile_file.name in ("__init__.py", "base.py"):
            continue

        module_name = profile_file.stem

        module = importlib.import_module(f"munibot.profiles.{module_name}")

        # Find all classes in the module that inherit from BaseProfile
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseProfile) and obj is not BaseProfile:
                profiles[module_name] = obj
                break

    external_profiles = {
        profile.name: profile.load()
        for profile in entry_points(group="munibot_profiles")
    }
    if external_profiles:
        for profile, class_ in external_profiles.items():
            if profile not in profiles:
                profiles[profile] = class_

    return profiles


def get_logger(name):

    logger = logging.getLogger(name)
    if "logging" in config:
        level = config["logging"].get("level", "WARNING")
        level = getattr(logging, level.upper(), 30)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(
            config["logging"].get(
                "format", "%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s"
            )
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
