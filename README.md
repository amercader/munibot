# Munibot

[![Tests](https://github.com/amercader/munibot/workflows/Tests/badge.svg)](https://github.com/amercader/munibot/actions)

Munibot is a friendly Mastodon bot that posts aerial or satellite imagery of administrative regions (tipically municipalities).


![munis_cat_scaled](https://user-images.githubusercontent.com/200230/102014660-6328cf00-3d57-11eb-86ec-183e8512538b.jpg)

It is written in a modular way so it's easy to customize to different data sources, via the implementation of profiles.

It currently powers the following Twitter accounts:

* [@munibot_es](https://twitter.com/munibot_es): All municipalities in Spain, shown in random order, with base aerial ortophotograhy from [PNOA IGN](https://pnoa.ign.es/).

* [@munibot_cat](https://twitter.com/munibot_cat): All municipalities in Catalonia, shown in random order, with base aerial ortophotograhy from [ICGC](https://www.icgc.cat/ca/Administracio-i-empresa/Medi-natural/Imatges-aeries-i-de-satel-lit/Ortofoto-convencional).

* [@communebot](https://twitter.com/communebot): All communes in France, shown in random order, with base aerial ortophotograhy from [IGN](https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html).


Here's how a sample post looks like:

<p align="center">

![example_post](https://github.com/user-attachments/assets/1798e999-e602-4665-80af-89546662e89c)

</p>

## Table of Contents

* [Usage](#usage)
   * [Installation](#installation)
   * [Configuration](#configuration)
   * [Running it](#running-it)
   * [Deploying it](#deploying-it)
* [Writing your own profile](#writing-your-own-profile)
* [Twitter Authorization](#twitter-authorization)
* [Development installation](#development-installation)
* [License](#license)


## Usage

### Installation

Munibot is available on PyPI and can be installed with `pip`. It is strongly recommended to install it in a [virtual environment](https://docs.python.org/3/tutorial/venv.html):

    python3 -m venv munibot
    source munibot/bin/activate

    pip install munibot

Or alternatively, using [`pipx`](https://pipxproject.github.io/pipx/):

    pipx install munibot


Munibot uses [Rasterio](https://rasterio.readthedocs.io) and [Fiona](https://fiona.readthedocs.io/en/latest/), which require GDAL. The wheels installed by pip on Linux (and macOS, although I have not tested it) include binaries for GDAL that cover munibot's need so it doesn't need to be installed separately. On other operating systems you might need to install GDAL.

### Configuration

Munibot uses an ini file for configuration. You can download the sample ini file included in this repository running:

    curl https://raw.githubusercontent.com/amercader/munibot/main/munibot.sample.ini -o munibot.ini

or:

    wget https://raw.githubusercontent.com/amercader/munibot/main/munibot.sample.ini -O munibot.ini

By itself munibot is not able to do much. You need to install an existing profile, or [write your own](#writing-your-own-profile).

To install a profile just install its Python package with pip:

    pip install munibot-es


### Running it

Once munibot is installed, you should be able to run

    munibot --help

Munibot assumes that the configuration ini file is located in the same folder the command is run on (and named "munibot.ini"). If that's not the case, you can pass the location of the configuration file with the `--config` or `-c`  arguments:

    munibot -c /path/to/munibot.ini

If at least a profile is available and all the necessary authorization tokens are available in the ini file (see [Twitter authorization](#twitter-authorization)) just run the following to post a new image:

    munibot post <profile-name>

If you only want to create the image without posting it use the `create` command:

    munibot create <profile-name>

### Deploying it

You don't need much to run munibot, just a system capable of running Python >= 3.6. Once installed, you probably want to schedule the sending of posts at regular intervals. An easy way available on Linux and macOS is `cron`. Here's an example configuration that you can adapt to your preferred interval and local paths (it assumes munibot was installed in a virtualenv in `/home/user/munibot`):

    # Post an image every 8 hours (~3 times a day)
    0 */8 * * * /home/user/munibot/bin/munibot --c /home/user/munibot/munibot.ini post cat >> /home/user/out/cat/munibot_cat.log 2>&1

You can adjust the log level in the munibot ini configuration file.

## Writing your own profile

Munibot is designed to be easy to customize to different data sources in order to power different bot accounts. This is done via *profile* classes. Profiles implement a few mandatory and optional properties and methods that provide the different inputs necessary to generate the posts. Munibot takes care of the common functionality like generating the final image and sending the post.

To see the actual methods that your profile should implement check the `BaseProfile` class in [`munibot/profiles/base.py`](https://github.com/amercader/munibot/blob/main/munibot/profiles/base.py). Here's a quick overview of what you should provide:

* The **geometry** of the boundary of a particular administrative unit (given an id). This can come from any place that can end up providing a GeoJSON-like Python dict: an actual GeoJSON file, PostGIS database or a [WFS](https://en.wikipedia.org/wiki/Web_Feature_Service) service.
* The **base image** (aerial photography or satellite imagery) covering the extent of the administrative unit (given the extent). [WMS](https://en.wikipedia.org/wiki/Web_Map_Service) services work really well for this as they allow to retrieve images of arbitrary extent and size.
* The **text** that should go along with the image in the post. Generally the name of the unit, plus some higher level unit for reference.
* A method that defines the **id** of the next unit that should be posted.
* Optionally, the **latitude and longitude** that should be added to the post.

Once you've implemented your profile class you can register using the `munibot_profiles` entry point in your package `setup.py` file:

```
"munibot_profiles": [
	"<profile_id>=<your_package>.profiles.:<YourProfileClass>",
]
```

You can check the following examples:

* Municipalities of Spain and Catalonia: [munibot_es](https://github.com/amercader/munibot_es)
* Communes of France: [communebot_fr](https://github.com/amercader/communebot_fr)



## Mastodon setup

TODO

## Development installation

Clone the repo and install the requirements:

    git clone https://github.com/amercader/munibot.git
    pip install -r requirements.txt
    pip install -r dev-requirements.txt

To run the tests:

    pytest

With coverage:

    pytest -v --cov=munibot --cov-report term-missing


## License

[MIT](/amercader/munibot/blob/master/LICENSE.txt)
