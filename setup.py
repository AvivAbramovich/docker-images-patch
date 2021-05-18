import os

import setuptools
import m2r


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_requirements(rel_path):
    return [line.strip('\n') for line in read(rel_path).splitlines()]


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


def get_long_description(rel_path):
    md = read(rel_path)
    return m2r.convert(md)


setuptools.setup(
    name='docker-patch',
    version=get_version('docker_patch/__init__.py'),
    author="Aviv Abramovich",
    author_email="AvivAbramovich@gmail.com",
    description="Patch docker images to fit your purposes and organization requirements",
    long_description=get_long_description('README.md'),
    url="https://github.com/AvivAbramovich/docker-patch",
    packages=setuptools.find_packages(),
    install_requires=get_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'docker-patch = docker_patch.__main__:main_cli'
        ],
    }
)