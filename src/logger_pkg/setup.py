from setuptools import setup

package_name = 'logger_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # INSTALL LAUNCH FILE!!!
        ('share/' + package_name + '/launch', ['launch/log_and_bag.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vihaan',
    maintainer_email='',
    description='Logging node + rosbag launcher',
    license='MIT',
    entry_points={
        'console_scripts': [
            'logging_node = logger_pkg.logging_node:main'
        ],
    },
)
