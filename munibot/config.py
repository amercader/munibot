import configparser
import os

from pkg_resources import iter_entry_points

config = {}


def load_config(path):

    if not os.path.exists(path):
        raise ValueError(
            """
INI file not found. It must be a "munibot.ini" file in the current directory,
otherwise pass the location with the "--config" parameter""".strip()
        )

    cp = configparser.ConfigParser()
    cp.read(path)
    for section in cp.sections():
        config[section] = dict(cp[section])


def load_profiles():

    profiles = {
        profile.name: profile.load()
        for profile in iter_entry_points("munibot_profiles")
    }

    return profiles
