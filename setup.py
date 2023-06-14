from distutils.core import setup

from setuptools import find_packages

setup(
    name='microservices_communication',
    version='1.0.27',
    packages=find_packages(),
    url='https://github.com/ksinn/django-microservices-communication',
    author='ksinn',
    author_email='ksinnd@gmail.com',
    description='Pub/Sub for service on django',
    long_description_content_type="text/markdown",
    install_requires=[
        "Django",
        "djangorestframework-camel-case",
        "pika"
    ],
    setup_requires=['wheel'],
)
