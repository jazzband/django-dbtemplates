import ast
import os
import io
from setuptools import setup, find_packages


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with io.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*parts):
    finder = VersionFinder()
    finder.visit(ast.parse(read(*parts)))
    return finder.version


setup(
    name='django-dbtemplates',
    version=find_version('dbtemplates', '__init__.py'),
    description='Template loader for templates stored in the database',
    long_description=read('README.rst'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='https://django-dbtemplates.readthedocs.io/',
    packages=find_packages(),
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
    ],
    install_requires=['django-appconf >= 0.4'],
)
