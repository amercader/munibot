# Munibot

![Tests](https://github.com/amercader/munibot/workflows/Tests/badge.svg)

Munibot is friendly Twitter bot that posts aerial or satellite imagery of administrative regions (tipically municipalities).


![munis_cat_scaled](https://user-images.githubusercontent.com/200230/102014660-6328cf00-3d57-11eb-86ec-183e8512538b.jpg)

It is written in a modular way so it's easy to customize to different data sources, via the implementation of profiles.

It currently powers the following Twitter accounts:

* [@munibot_es](https://twitter.com/munibot_es): All municipalities in Spain, shown in random order, with base aerial ortophotograhy from [PNOA IGN](https://pnoa.ign.es/).

* [@munibot_cat](https://twitter.com/munibot_cat): All municipalities in Catalonia, shown in random order, with base aerial ortophotograhy from [ICGC](https://www.icgc.cat/ca/Administracio-i-empresa/Medi-natural/Imatges-aeries-i-de-satel-lit/Ortofoto-convencional).


Here's how a sample tweet looks like:

<p align="center">

![example_tweet](https://user-images.githubusercontent.com/200230/102015071-89e80500-3d59-11eb-8685-12967e9276d8.jpg)

</p>


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

If you want to try the `es` and `cat` profiles included in the main library, you'll also need the backend SQLite database:

    wget https://github.com/amercader/munibot/raw/main/data/munis_esp.sqlite

Adapt the `db_path` entries in the configuration to the path where you saved the database.


## Running it

Once munibot is installed, you should be able to run

    munibot --help

Munibot assumes that the configuration ini file is located in the same folder the command is run on (and named "munibot.ini"). If that's not the case, you can pass the location of the configuration file with the `--config` or `-c`  arguments:

    munibot -c /path/to/munibot.ini

If at least a profile is available and all the necessary authorization tokens are available in the ini file (TODO) just run the following to tweet a new image:

    munibot tweet es

If you only want to create the image without tweeting it use the `create` command:

    munibot create es

## Deploying it

TODO

## Twitter Authorization

TODO



## License

[MIT](/amercader/munibot/blob/master/LICENSE.txt)
