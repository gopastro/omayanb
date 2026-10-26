from setuptools import setup, find_packages
import re

modcontents = open('omayanb/__init__.py').read()
version = re.search(r"__version__ = '([^']*)'",modcontents).group(1)

setup(
    name='omayanb',
    version=version,
    description='OMAyA Narrowband IF Processor Monitor and Control',
    author='Gopal Narayanan',
    author_email='gopal@astro.umass.edu',
    install_requires=['numpy', 'matplotlib', 'pandas'],
    packages=['omayanb'],
    #scripts=[]
)
