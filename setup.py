from setuptools import setup, find_packages

from prakasha import meta
from prakasha.util import dist


setup(
    name=meta.display_name,
    version=meta.version,
    description=meta.description,
    author=meta.author,
    author_email=meta.author_email,
    url=meta.url,
    license=meta.license,
    long_description=dist.catReST(
        "docs/PRELUDE.rst",
        "README.rst",
        "docs/DEPENDENCIES.rst",
        "docs/INSTALL.rst",
        "docs/USAGE.rst",
        "TODO",
        "docs/HISTORY.rst",
        stop_on_errors=True,
        out=True),
    packages=find_packages() + ["twisted.plugins"],
    package_data={
        "twisted": ['plugins/prakasha.py']
        },  
    install_requires=[
        "twisted",
        "PyOpenSSL",
        "pycrypto",
        "pyasn1",
        "DreamSSH",
        "docutils",
        ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    )
