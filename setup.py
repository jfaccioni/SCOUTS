from setuptools import find_packages, setup


setup(
    name="SCOUTS",
    version='1.0.0',
    description="Single Cell OUTlier Selector",
    author="Juliano Luiz Faccioni",
    author_email="julianofaccioni@gmail.com",
    mantainer="Juliano Luiz Faccioni",
    mantainer_email="julianofaccioni@gmail.com",
    url="http://www.ufrgs.br/labsinal/SCOUTS/index.html",
    download_url="https://scouts.readthedocs.io/en/master/install.html",
    project_urls={
        'Bug Tracker': 'https://github.com/jfaccioni/scouts/issues',
        'Documentation': 'https://scouts.readthedocs.io/en/master/',
        'Source Code': 'https://github.com/jfaccioni/scouts'
    },
    long_description="SCOUTS is a tool that quickly finds outliers in your single-cell data, generating information about your population organized by target molecules. SCOUTS takes your single-cell input and generates output files containing only outliers. The method used by SCOUTS to subset the population and find the outliers is customizable through the program's interface.",
    license="MIT",
    platforms="any",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "pyside2",
        "openpyxl",
        "xlrd"
    ],
    entry_points={
        'console_scripts': [
            'scouts=src.gui:main',
            'scouts-violins=scripts.gui_violins:main'
        ]
    }
)
