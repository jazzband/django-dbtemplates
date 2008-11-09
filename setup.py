from distutils.core import setup

setup(
    name='django-dbtemplates',
    version='0.5.1',
    description='Template loader for database stored templates',
    long_description=open('docs/overview.txt').read(),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://www.bitbucket.org/jezdez/django-dbtemplates/wiki/',
    download_url='http://www.bitbucket.org/jezdez/django-dbtemplates/get/v0.5.1.gz',
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
