# SCOUTS - Single Cell OUTlier Selector

<p align="middle">
<img src="doc/\_static/cells-white.png" alt="SCOUTS" width="400"/>
</p>

**SCOUTS** is a tool that quickly finds outliers in your single-cell data, generating information about your population organized by target molecules.

SCOUTS takes your single-cell input and generates output files containing only outliers. The method used by SCOUTS to subset the population and find the outliers is customizable through the program's interface.

## Why SCOUTS?
Many single cell analysis pipelines require some level of programming knowledge in order to be used. While some great tools for languages like R, Python and Julia have been developed, the entry-level barrier of programming is still intimidating for many scientists starting on the field of singe-cell analysis. With this in mind, we developed SCOUTS to simplify this process. Through a desktop application, the user is able to choose the parameters for the outlier selection, and leave the hard work of programatically subsetting the data to SCOUTS.

Of course, being a open-source project distributed under the MIT license, those with a more robust programming background are welcome to read the source code of SCOUTS and adapt it to their specific needs.

## Getting Started
SCOUTS is available both as a **binary stand-alone release** and as a **Python package**, which can be downloaded from this repository and run with your local Python interpreter.

### Download as an executable binary
SCOUTS is available as a binary file, which bundles all information needed to run the program. Simply download the file for your OS and execute it.

* [Windows](https://github.com/jfaccioni/scouts/tree/master/executables/windows)
* [Linux](https://github.com/jfaccioni/scouts/tree/master/executables/linux)
* MacOS (coming soon!)

Be aware that this is an experimental release of SCOUTS and, as such, is prone to bugs and errors. We kindly suggest you to [report](https://github.com/jfaccioni/scouts/issues) any problems that you come across.

#### Installation from this repository
SCOUTS is written in Python 3.6. If your system does not have Python 3.6 or higher, [click here to download it](https://www.python.org/downloads/).

Third-party modules used by SCOUTS:
* [Numpy](http://www.numpy.org/)
* [Pandas](https://pandas.pydata.org/)
* [PySide2](https://pypi.org/project/PySide2/)
* [Openpyxl](https://openpyxl.readthedocs.io/en/stable/)


A full list of the third-party packages in a known working environment are listed in the [environment.yml](environment.yml) file (tested in Ubuntu 18.04).

#### Install with Conda
The easiest way to install SCOUTS is using a Python package manager such as [Conda](https://conda.io/docs/).

* clone the repository into your local machine:

```
$ git clone https://github.com/jfaccioni/scouts
```

* cd into the repository:

```
$ cd scouts
```

* use Conda to create a new environment with the required dependencies:

```
$ conda env create --name scouts --file environment.yml
```

* activate the newly created environment:

```
$ conda activate scouts
```

* finally, run SCOUTS using your Python interpreter:

```
$ python scouts.py
```

#### Install from source
Of course, you can also download the source code and use pip to install the required packages (if you already have them in your system, you won't need to install anything).

## Usage
Information about how to use SCOUTS can be found in this section.

### Quick Start

When you start SCOUTS, you should see this:

<p align="middle">
<img src="doc/\_static/SCOUTS_main.png" alt="SCOUTS main window" scale="90%"/>
</p>

These are your main options for the analysis:

<p align="middle">
<img src="doc/\_static/SCOUTS_info.png" alt="SCOUTS main window - information" scale="90%"/>
</p>

Sample names are particularly important (if the application does not find a given sample, it warns you and stops the analysis). Click here to select and edit them:

<p align="middle">
<img src="doc/\_static/SCOUTS_samples.png" alt="SCOUTS main window - sample button" scale="90%"/>
</p>

In this window you can inform your sample names. You don't have to use the full sample name - any identifier exclusive to each sample is enough, as long as it is part of your samples in the input file. Don't forget to add a control sample, too.

<p align="middle">
<img src="doc/\_static/SCOUTS_samplepage.png" alt="sample selection window" scale="90%"/>
</p>

[How SCOUTS works](https://scouts.readthedocs.io/en/master/work.html) has a detailed explanation of how the program reads and parses sample names.

You can also gate your samples, if you want:

<p align="middle">
<img src="doc/\_static/SCOUTS_gates.png" alt="SCOUTS main window - gates button" scale="90%"/>
</p>

The gating functionality works differently for mass cytometry and scRNA-seq samples. Refer to [How SCOUTS works](https://scouts.readthedocs.io/en/master/work.html) for details.

<p align="middle">
<img src="doc/\_static/SCOUTS_gatepage.png" alt="Gates selection window" scale="90%"/>
</p>

Ready? Click **Run**!

<p align="middle">
<img src="doc/\_static/SCOUTS_run.png" alt="SCOUTS main window - run button" scale="90%"/>
</p>

### Documentation
[Read the full SCOUTS documentation here](https://scouts.readthedocs.io/en/master/).

### FAQ
[Frequently asked questions can be found here](https://scouts.readthedocs.io/en/master/faq.html).


## Authors
* **Juliano Faccioni** - *Programming and GUI development* - [GitHub](https://github.com/jfaccioni) - [LinkedIn](https://www.linkedin.com/in/juliano-faccioni-9b2133167)
* **Giovana Onzi** - *Concept and testing* -  [LinkedIn](https://www.linkedin.com/in/giovana-onzi-ba222895/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgements
* Prof. Dr. Guido Lenz
* Prof. Dr. Harley Kornblum
* CAPES/CNPq
* NIH
