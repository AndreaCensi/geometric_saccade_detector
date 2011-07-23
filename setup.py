from setuptools import setup

setup(
    name='geometric_saccade_detector',
	version="1.1",
    package_dir={'':'src'},
    py_modules=['snp'],
    install_requires=['flydra', 'matplotlib', 'PyContracts'],
    entry_points={
         'console_scripts': [
           'geo_sac_detect  = geometric_saccade_detector.detect:main',
           'geo_sac_compact  = geometric_saccade_detector.conversions.compact_data:main',
           'geo_sac_to_flydradb  = geometric_saccade_detector.conversions.to_flydra_db:main',
           'geo_sac_detect_flydra  = geometric_saccade_detector.main_flydra_db_detect:main',
        ]
      },
      
    author="Andrea Censi",
    author_email="andrea@cds.caltech.edu",
    description="This package provides functions to detect fly saccades"\
        "from Flydra data.",
    license="GPL",
    keywords="saccade fly flies filtering drosophila flydra sachertorte",
    url="http://github.com/AndreaCensi/geometric_saccade_detector"
)


