from setuptools import find_packages
from setuptools import setup

NAME = "braze-client"
VERSION = "2.2.0"

REQUIRES = ["requests >=2.21.0, <3.0.0", "tenacity >=5.0.0, <6.0.0"]

EXTRAS = {"dev": ["tox"]}

setup(
    name=NAME,
    version=VERSION,
    description="Braze Python Client",
    author_email="azh@hellofresh.com",
    keywords=["Appboy", "Braze"],
    install_requires=REQUIRES,
    extras_require=EXTRAS,
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
    ],
)
