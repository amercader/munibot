import configparser
import os
import logging

from pkg_resources import iter_entry_points

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

    profiles = {
        profile.name: profile.load()
        for profile in iter_entry_points("munibot_profiles")
    }

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
