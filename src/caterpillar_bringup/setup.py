import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'caterpillar_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Register the package in the ament index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # Include package.xml
        ('share/' + package_name, ['package.xml']),
        
        # INSTALLATION CODE FOR LAUNCH FILES
        # Installs all .launch.py files from the 'launch' folder into share/package_name/launch
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),

        # INSTALLATION CODE FOR CONFIG FILES
        # Installs all .yaml files from the 'config' folder into share/package_name/config
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mars22',
    maintainer_email='work.arpit.sri@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)