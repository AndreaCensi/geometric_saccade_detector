from setuptools import setup

setup(
    name='geometric_saccade_detector',
	version="1.0",
    package_dir={'':'src'},
    py_modules=['snp'],
    install_requires=['flydra', 'matplotlib'],
    entry_points={
         'console_scripts': [
           'geo_sac_detect  = geometric_saccade_detector.detect:main'
        ]
      },
      
    author="Andrea Censi",
    author_email="andrea@cds.caltech.edu",
    description="This package provides functions to detect fly saccades"\
        "from Flydra data.",
    license="GPL",
    keywords="saccade fly flies filtering drosophila flydra sachertorte",
    url="https://github.com/AndreaCensi/geometric_saccade_detector"
)


