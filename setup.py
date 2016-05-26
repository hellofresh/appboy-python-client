from setuptools import setup, find_packages

NAME = "appboy-client"
VERSION = "0.0.1"

REQUIRES = []

setup(
    name=NAME,
    version=VERSION,
    description="Appboy python client",
    author_email="azh@hellofresh.com",
    keywords=["HelloFresh", "Appboy"],
    install_requires=REQUIRES,
    packages=find_packages()
)
