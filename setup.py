"""
Insta485 python package configuration.

Andrew DeOrio <awdeorio@umich.edu>
"""

from setuptools import setup

setup(
    name='gnarly-climber',
    version='0.1.0',
    packages=['gnarly-climber'],
    include_package_data=True,
    install_requires=[
        'arrow==0.15.7',
        'bs4==0.0.1',
        'Flask==1.1.2',
        'html5validator==0.3.3',
        'nodeenv==1.4.0',
        'pycodestyle==2.6.0',
        'pydocstyle==5.0.2',
        'pylint==2.5.3',
        'pytest==5.4.3',
        'requests==2.24.0',
        'selenium==3.141.0',
    ],
    python_requires='>=3.6',
)
