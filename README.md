# SCOUT - Single Cell OUTlier analysis

<p align="middle">
<img src="/images/cells-white.png" alt="SCOUT" width="400"/>
</p>

**SCOUT** is a tool that quickly finds outliers in your single-cell data, generating information about your population organized by targeted molecules.

## Getting Started
SCOUT is available both as a **binary stand-alone release** and as a **Python package**, which can be downloaded from this repository and run with your local Python interpreter.

### Download as an executable binary
SCOUT is available as a binary file, which bundles all information needed to run the program. Simply download the file for your OS and execute it.

* [Windows](link) (v1.0)
* [Mac](link) (v1.0)
* [Linux](link) (v1.0)

Be aware that this is an experimental release of SCOUT and, as such, is prone to bugs and errors. We kindly suggest you to [report](https://github.com/jfaccioni/scout/issues) any problems that you come across.

#### Installation from this repository
SCOUT is written in Python 3.6. If your system does not have Python 3.6 or higher, [click here to download it](https://www.python.org/downloads/).

Third-party modules used by SCOUT:
* [Numpy](http://www.numpy.org/)
* [Pandas](https://pandas.pydata.org/)
* [Pyqt5](https://pypi.org/project/PyQt5/)


A full list of the third-party packages in a known working environment are listed in the [environment.yml](environment.yml) file (tested in Ubuntu 18.04).

#### Install with Conda
The easiest way to install SCOUT is using a Python package manager such as [Conda](https://conda.io/docs/).

* clone the repository into your local machine:

```
$ git clone https://github.com/jfaccioni/scout
```

* cd into the repository:

```
$ cd scout
```

* use Conda to create a new environment with the required dependencies:

```
$ conda env create --name scout --file environment.yml
```

* activate the newly created environment:

```
$ conda activate scout
```

* finally, run SCOUT using your Python interpreter:

```
$ python scout.py
```

#### Install from source
Of course, you can also download the source code and use pip to install the required packages (if you already have them in your system, you won't need to install anything).

## Usage
Information about how to use SCOUT can be found in this section.

### Quick Start
Open the application and select which analysis to perform (e.g. Cytof):

<p align="middle">
<img src="/images/mainapp.png" alt="Main App Window" width="400"/>
</p>

Select your input and output:

<p align="middle">
<img src="/images/iocytof.png" alt="Cytof Analysis Window" width="600"/>
</p>

Sample names are particularly important (if the application does not find a given sample, it throws an error):

<p align="middle">
<img src="/images/samplenames.png" alt="Sample Selection Window" width="650"/>
</p>

The [full documentation](www.google.com) explains how the program works with sample names.

Next, select your analysis parameters:

<p align="middle">
<img src="/images/cytof_analysis.png" alt="Cytof Parameters" width="650"/>
</p>

Ready? Click **Run**!

### Documentation
[Read the full SCOUT documentation here](link).

### FAQ
[Frequently asked questions can be found here](link).


## Authors
* **Juliano Faccioni** - *Programming and GUI development* - [GitHub](https://github.com/jfaccioni) - [LinkedIn](https://www.linkedin.com/in/juliano-faccioni-9b2133167)
* **Giovana Onzi** - *Concept and testing* -  [LinkedIn](https://www.linkedin.com/in/giovana-onzi-ba222895/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
* Prof. Dr. Guido Lenz
* Prof. Dr. Harley Kornblum
* CAPES/CNPq
* NIH <project-no>
