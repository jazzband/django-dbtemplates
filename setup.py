from distutils.core import setup

setup(
    name='dbtemplates',
    version='0.3.0',
    description='Template loader for database stored templates',
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://code.google.com/p/django-databasetemplateloader/',
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
