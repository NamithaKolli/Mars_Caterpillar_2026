from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'realsense_vslam'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Package.xml
        ('share/' + package_name, ['package.xml']),

        # Launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        
        # Map files
        # (os.path.join('share', package_name, 'map'),
            # glob('launch/*.db')),
            
        # RViz files
        (os.path.join('share', package_name, 'rviz'),
            glob('launch/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mars22',
    maintainer_email='mars22@todo.todo',
    description='RealSense D455 RTAB-Map VSLAM launch package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [],
    },
)
