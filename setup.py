import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="munibot",
    version="0.0.1",
    author="Adrià Mercader",
    author_email="amercadero@gmail.com",
    description="A Twitter bot that tweets aerial imagery pictures of municipalities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amercader/munibot",
    packages=setuptools.find_packages(),
    install_requires=[
        "fiona>=1.8,<1.19",
        "rasterio>=1.1",
        "shapely>=1.7,<1.8",
        "owslib>=0.20.0,<0.21",
        "Pillow>=8,<9",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["munibot=munibot.munibot:main"],
        "munibot_profiles": [
            "es=munibot.profiles.es:MuniBotEs",
            "cat=munibot.profiles.cat:MuniBotCat",
        ],
    },
)
