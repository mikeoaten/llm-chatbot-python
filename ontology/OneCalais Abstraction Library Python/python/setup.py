from distutils.core import setup
from distutils.command.install_data import install_data

import os
import sys

    
cmdclasses = {'install_data': install_data} 

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
oneCalais_dir = 'onecalais'

for dirpath, dirnames, filenames in os.walk(oneCalais_dir):
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "CalaisModel",
    version = '8.0-SNAPSHOT',
    description = 'CalaisModel is an Abstraction layer for the RDF',
    license = 'MIT',
    author = 'Oren Hazai, Benny Vaknin',
    packages = packages,
    author_email = 'benny.vaknin@thomsonreuters.com, oren.hazai@thomsonreuters.com',
    cmdclass = cmdclasses,
    data_files = data_files,
    
)
