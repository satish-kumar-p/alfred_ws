import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'simple_simulation_node'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='satheesh',
    maintainer_email='satheesh.kumar@redanttechsys.com',
    description='Node for simulating battery, boot checks, mode, table logging, and navigation commands.',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'simple_simulation_node = simple_simulation_node.simple_simulation_node:main'
        ],
    },
)
