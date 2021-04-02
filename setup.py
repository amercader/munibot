import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    install_requires = f.readlines()

setuptools.setup(
    name="munibot",
    version="0.0.3",
    author="Adrià Mercader",
    author_email="amercadero@gmail.com",
    description="A Twitter bot that tweets aerial imagery pictures of municipalities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amercader/munibot",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["munibot=munibot.munibot:main"],
    },
)
