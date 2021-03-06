# coding=utf-8
from distutils.core import setup

setup(
    name='mongorm',
    version='0.2.0',
    author='Chris Mitchell',
    author_email='milchardo@hotmail.co.uk',
    license='LICENSE.txt',
    description='ORM - Mongodb to Python classes',
    long_description=open('README.txt').read(),
    packages=['mongorm', 'mongorm.tests'],
    install_requires=[
        "pymongo==2.5",
    ],
)
