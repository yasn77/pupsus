import os
import shutil
from setuptools import setup

README = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../README.md")

def readme():
    if os.path.isfile(README):
        shutil.copy(README, 'README.txt')
        return open(README).read()
    else:
        return open('README.txt').read()

install_requires = [
                    'argparse',
                    'requests',
                    'requests_cache',
                    'semantic_version',
                    'PyYAML'
                   ]
setup(
    name = "pupsus",
    version = "0.0.4",
    author = "Yasser Nabi",
    author_email = "yassersaleemi@gmail.com",
    description = ("Manage Puppet modules with Sonatype Nexus"),
    license = "GPLv2+",
    url = "https://github.com/yasn77/pupsus",
    packages=['pupsus'],
    install_requires=install_requires,
    long_description=readme(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    ],
   entry_points = {
                  "console_scripts": [
                                      'pupsus = pupsus.pupsus:main',
                                      ]
                  },
    data_files=[
                ('/etc/pupsus', ['test/resources/pupsus.ini'])
               ]
)
