from distutils.core import setup

setup(
    name='django-dbtemplates',
    version='0.4.6',
    description='Template loader for database stored templates',
    long_description=open('README.rst').read(),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://code.google.com/p/django-dbtemplates/',
    scripts=['dbtemplates/sync_templates.py',],
    packages=[
        'dbtemplates',
        'dbtemplates.management',
        'dbtemplates.management.commands'
    ],
    package_dir={'dbtemplates': 'dbtemplates'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ]
)
