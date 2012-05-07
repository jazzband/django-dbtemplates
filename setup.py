import os
import re
import codecs
from setuptools import setup, find_packages


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-dbtemplates',
    version=find_version('dbtemplates', '__init__.py'),
    description='Template loader for templates stored in the database',
    long_description=read('README.rst'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://django-dbtemplates.readthedocs.org/',
    packages=find_packages(exclude=['example']),
    zip_safe=False,
    package_data={
        'dbtemplates': [
            'locale/*/LC_MESSAGES/*',
            'static/dbtemplates/css/*.css',
            'static/dbtemplates/js/*.js',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
    ],
    install_requires=['django-appconf >= 0.4'],
)
