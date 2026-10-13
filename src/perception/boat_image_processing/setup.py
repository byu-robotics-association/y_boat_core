from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'boat_image_processing'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Stephen Day',
    maintainer_email='sday1804@byu.edu',
    description='Package for handling the YOLO model and image processing for the BYU RoboBoat.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'object_detector = boat_image_processing.object_detector:main'
        ],
    },
)
