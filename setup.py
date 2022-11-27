import os

from setuptools import setup




# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = '0.0.1'
requires = [
    'Django<=4.1',
    'six',
]

setup(
    name='nuitka-django',
    version=version,
    packages=['nuitka_django'],
    python_requires=">=2.7",
    install_requires=requires,
    include_package_data=True,
    license='MIT License',
    description='build command for django to easly build django project with nuitka',
    url='https://github.com/patriotyk/nuitka-django',
    author='Serhiy Stetskovych',
    author_email='patriotyk@gmail.com',
    classifiers=[

    ],
)
