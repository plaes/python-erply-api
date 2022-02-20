from setuptools import setup

# Metadata is in setup.cfg. This file is mostly for Github's dependency graph.
setup(
    name='ErplyAPI',
    install_requires=['requests[security]>=2.6.0'],
    py_modules = ['erply_api']
)
