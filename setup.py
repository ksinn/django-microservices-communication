from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    version='2.6.2',
    name='django-microservices-communication',
    packages=find_packages(),
    url='https://github.com/ksinn/django-microservices-communication',
    author='ksinn',
    author_email='ksinnd@gmail.com',
    description='Pub/Sub for microservice on django',
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=[
        "Django",
        "djangorestframework",
        "djangorestframework-camel-case",
        "pika",
        "requests",
        "pytz",
    ],
    setup_requires=['wheel'],
)
