#!/usr/bin/env python
"""
Erply-API
---------

Python wrapper for Erply API
"""
from distutils.core import setup

setup(
    name='ErplyAPI',
    version='0.2015.01.16',
    description='Python wrapper for Erply API',
    license='BSD',
    author='Priit Laes',
    author_email='plaes@plaes.org',
    long_description=__doc__,
    install_requires=['requests'],
    py_modules=['erply_api'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'Topic :: Software Development :: Libraries',
    ]
)
