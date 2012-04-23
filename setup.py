from setuptools import setup

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
    packages=dist.findPackages(meta.library_name),
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
    install_requires=[
        "twisted",
        "PyOpenSSL",
        "pycrypto",
        "pyasn1",
        "docutils",
        ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    )
