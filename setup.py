import json
from setuptools import setup, find_namespace_packages

with open('k8svimdriver/pkg_info.json') as fp:
    _pkg_info = json.load(fp)

with open("DESCRIPTION.md", "r") as description_file:
    long_description = description_file.read()

setup(
    name='k8s-vim-driver',
    version=_pkg_info['version'],
    author='Accanto Systems',
    description='K8s implementation of a VIM driver',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/accanto-systems/k8s-vim-driver",
    packages=find_namespace_packages(include=['k8svimdriver*']),
    include_package_data=True,
    install_requires=[
        'ignition-framework{0}'.format(_pkg_info['ignition-version']),
        'heat-translator>=1.3.0,<2.0',
        'tosca-parser>=1.4.0,<2.0',
        'kubernetes>=9.0.0',
        'python-common-cache>=0.1',
        'uwsgi>=2.0.18',
        'gunicorn>=19.9.0'
    ],
    entry_points='''
        [console_scripts]
        k8s-dev=k8svimdriver.__main__:main
    ''',
    scripts=['k8svimdriver/bin/k8svd-uwsgi', 'k8svimdriver/bin/k8svd-gunicorn', 'k8svimdriver/bin/k8svd']
)