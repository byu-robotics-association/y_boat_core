from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'boat_perception_fusion'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Corban Thompson',
    maintainer_email='corbant25@gmail.com',
    description='Nodes for fusing visual data into 3d object detections',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'object_association_node = boat_perception_fusion.object_association_node:main'
        ],
    },
)
