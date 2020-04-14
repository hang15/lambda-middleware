from setuptools import setup

import lambda_middleware

setup(
    name='lambda_middleware',
    version=lambda_middleware.__version__,

    description='A framework for lambda middlewares',

    keywords='lambda middleware aws',

    packages=['lambda_middleware'],
)
