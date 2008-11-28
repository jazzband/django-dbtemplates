from distutils.core import setup

setup(
    name='django-dbtemplates',
    version=__import__('dbtemplates').__version__,
    description='Template loader for database stored templates with extensible cache backend',
    long_description=open('docs/overview.txt').read(),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://github.com/jezdez/django-dbtemplates/wikis/',
    download_url='http://github.com/jezdez/django-dbtemplates/tarball/0.5.3',
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
        'Framework :: Django',
    ]
)
