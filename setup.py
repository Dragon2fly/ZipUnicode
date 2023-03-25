from setuptools import setup
from zip_unicode import __version__

with open('README.md', encoding='utf8') as fi:
    long_description = fi.read()

setup(
    name='ZipUnicode',
    version=__version__,
    packages=['zip_unicode'],
    url='https://github.com/Dragon2fly/ZipUnicode',
    license='MIT',
    entry_points={
        'console_scripts': [
            'zipu=zip_unicode.main:entry_point',
        ],
    },
    platforms=["Any platform -- don't need Windows"],
    author='Nguyen Ba Duc Tin',
    author_email='nguyenbaduc.tin@gmail.com',
    description='Fix unreadable file names when extracting zip file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'chardet>=3.0.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Home Automation',
        'Topic :: Office/Business',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities'
    ],
    python_requires=">=3.6",
)
