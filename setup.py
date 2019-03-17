# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages
from wscrape import (
    NAME,
    VERSION,
    AUTHOR,
    AUTHOR_EMAIL,
    DESCRIPTION,
)

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    packages = find_packages(),
    # data_files = ['wscrape/spiders/config.toml'],
    include_package_data = True,
    entry_points = {'scrapy': ['settings = wscrape.settings']},
)
