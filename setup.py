from setuptools import setup, find_packages
from distutils.extension import Extension

import numpy as np


__version__ = '0.1'


def read_requirements():
    import os


    path = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(path, 'requirements.txt')
    try:
        with open(requirements_file, 'r') as req_fp:
            requires = req_fp.read().split()
    except IOError:
        return []
    else:
        return [require.split() for require in requires]


setup(name='overlandflow',
      version=__version__,
      description='Rain + overland flow + infiltration',
      author='Eric Hutton',
      author_email='huttone@colorado.edu',
      url='https://github.com/mcflugen/overland_flow',
      install_requires=read_requirements(),
      setup_requires=['setuptools', ],
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'overlandflow=overlandflow.model:OverlandFlowModel.main',
          ],
      },
)
