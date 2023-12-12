from distutils.core import setup

from setuptools import find_packages

setup(
    version='2.1.1',
    name='django-microservices-communication',
    packages=find_packages(),
    url='https://github.com/ksinn/django-microservices-communication',
    author='ksinn',
    author_email='ksinnd@gmail.com',
    description='Pub/Sub for service on django',
    long_description_content_type="text/markdown",
    install_requires=[
        "Django",
        "djangorestframework",
        "djangorestframework-camel-case",
        "pika",
        "requests",
    ],
    setup_requires=['wheel'],
)
