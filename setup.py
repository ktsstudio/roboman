from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
version = '0.2.0'
modules = ['tornado', 'requests', 'tornkts']
setup(
    name='roboman',
    version=version,
    description='Framework based on Tornado for creation of powerful bots',
    long_description='Framework based on Tornado for creation of powerful bots',
    author='KTS',
    author_email='roboman@ktsstudio.ru',
    url='https://github.com/KTSStudio/roboman',
    download_url='https://github.com/KTSStudio/roboman/tarball/v' + version,
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='roboman telegram bot',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=modules,
)
