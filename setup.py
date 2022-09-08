# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: AGPL-3.0-or-later

from setuptools import setup

setup(
    name='podcastify',
    version='0.0.1',
    url='https://github.com/t184256/podcastify',
    author='Alexander Sosedkin',
    author_email='monk@unboiled.info',
    description="podcast generator based on yt-dlp",
    packages=[
        'podcastify',
    ],
    install_requires=['flask', 'feedgen', 'ruamel-yaml'],
    #scripts=['podcastify/__main__.py'],
    entry_points={
        'console_scripts': [
            'podcastify = podcastify.main:main',
        ],
    },
)
