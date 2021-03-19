from setuptools import setup


def _get_version():
    with open('VERSION') as fd:
        return fd.read().strip()

setup(
    name='keras-api-python',
    version=_get_version(),
    packages=['webapi'],
    package_dir={'': './'},
    py_modules=['webapi']
)
