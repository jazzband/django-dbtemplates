import os
import io
from setuptools import setup, find_packages


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with io.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    name="django-dbtemplates-iplweb",
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    description="Template loader for templates stored in the database",
    long_description=read("README.rst"),
    author="Jannis Leidel",
    author_email="jannis@leidel.info",
    url="https://django-dbtemplates.readthedocs.io/",
    packages=find_packages(),
    zip_safe=False,
    package_data={
        "dbtemplates": [
            "locale/*/LC_MESSAGES/*",
            "static/dbtemplates/css/*.css",
            "static/dbtemplates/js/*.js",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django",
    ],
    python_requires='>=3.6',
    install_requires=["django-appconf >= 0.4"],
)

