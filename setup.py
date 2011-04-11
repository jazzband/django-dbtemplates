from setuptools import setup, find_packages

setup(
    name='django-dbtemplates',
    version=__import__('dbtemplates').__version__,
    description='Template loader for templates stored in the database',
    long_description=open('README.rst').read(),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://django-dbtemplates.readthedocs.org/',
    packages=find_packages(exclude=['example']),
    zip_safe=False,
    package_data = {
        'dbtemplates': [
            'locale/*/LC_MESSAGES/*',
            'static/dbtemplates/css/*.css',
            'static/dbtemplates/js/*.js',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
