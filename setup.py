import re

import setuptools


PACKAGE_NAME = 'cgiproxy'
FILE_NAME = PACKAGE_NAME + '/__init__.py'
VERSION = re.search(
    "__version__ = ['\"]([^'\"]+)['\"]", open(FILE_NAME, 'r').read()).group(1)

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description='The simple HTTP proxy.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/Datamart/CGI-Proxy',
    author='Valentin Podkamennyi, Alex Krailo',
    # author_email='Valentin Podkamennyi <valentin@dtm.io>, Alex Krailo <alex@dtm.io>',
    license='Apache 2.0',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
