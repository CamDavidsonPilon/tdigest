#!/usr/bin/env python
import os
from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='tdigest',
      version='0.1.1',
      description='T-Digest data structure',
      author='Cam Davidson-pilon',
      author_email='cam.davidson.pilon@gmail.com',
      url='https://github.com/CamDavidsonPilon/tdigest',
      packages=['tdigest'],
      long_description=read('README.md'),
      install_requires=[
          "bintrees",
      ],
      classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        ],
      license="MIT",
      keywords='percentile, median, data structure, quantitle, distributed, qdigest, tdigest',
      package_data={
        "tdigest": [
            "../README.md",
            "../LICENSE.txt",
            "../MANIFEST",
        ]
      },
)
