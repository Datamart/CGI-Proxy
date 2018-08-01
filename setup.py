import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cgi-proxy',
    version='10.26',
    description='The simple HTTP proxy.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Datamart/CGI-Proxy',
    author='Valentin Podkamennyi, Alex Krailo',
    # author_email='Valentin Podkamennyi <valentin@dtm.io>, Alex Krailo <alex@dtm.io>',
    license='Apache 2.0',
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    )
)