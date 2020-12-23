from setuptools import setup, find_packages

NAME = "appboy-client"
VERSION = "0.0.1"

REQUIRES = [
    'requests==2.22.0',
]

EXTRAS = {
    'dev': [
        'tox',
    ],
}

setup(
    name=NAME,
    version=VERSION,
    description="Appboy python client",
    author_email="azh@hellofresh.com",
    keywords=["HelloFresh", "Appboy"],
    install_requires=REQUIRES,
    extras_require=EXTRAS,
    packages=find_packages(exclude=('tests',)),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ],
)
