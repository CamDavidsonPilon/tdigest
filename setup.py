#!/usr/bin/env python
import os
from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='tdigest',
      version='0.0.1',
      description='T-Digest data structure',
      author='Cam Davidson-pilon',
      author_email='cam.davidson.pilon@gmail.com',
      url='https://github.com/CamDavidsonPilon/tdigest',
      packages=['tdigest'],
      long_description=read('README.md'),
      install_requires=[
          "bintrees",
      ],
      )
