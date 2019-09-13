from setuptools import find_packages, setup


VERSION = "0.1.0"

LONG_DESCRIPTION = """SCOUTS is a tool that quickly finds outliers in your single-cell data, generating information
about your population organized by target molecules. SCOUTS takes your single-cell input and generates output files
containing only outliers. The method used by SCOUTS to subset the population and find the outliers is customizable
through the program's interface."""

setup(
    name="scouts",
    version=VERSION,
    description="Single Cell Outlier Selector",
    author="Juliano Luiz Faccioni",
    author_email="julianofaccioni@gmail.com",
    mantainer="Juliano Luiz Faccioni",
    mantainer_email="julianofaccioni@gmail.com",
    # url="http://www.ufrgs.br/labsinal/scouts/index.html",  wait for OK
    download_url="https://scouts.readthedocs.io/en/master/install.html",
    project_urls={
        'Bug Tracker': 'https://github.com/jfaccioni/scouts/issues',
        'Documentation': 'https://scouts.readthedocs.io/en/master/',
        'Source Code': 'https://github.com/jfaccioni/scouts'
    },
    long_description=LONG_DESCRIPTION,
    license="MIT",
    platforms="any",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy",
        "pandas",
        "pyside2",
        "openpyxl",
        "xlrd",
    ],
    extras_require={
        'violins': ['matplotlib', 'seaborn']
    },
    entry_points={
        'console_scripts': [
            'scouts=src.gui:main',
            'scouts-violins=src.gui_violins:main [violins]'
        ]
    }
)
