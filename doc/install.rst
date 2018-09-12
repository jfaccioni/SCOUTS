Installation
============

SCOUTS is available both as a **binary stand-alone release** and as a **Python package**, which can be downloaded from this repository and run with your local Python interpreter.

Download as a binary executable
-------------------------------
SCOUTS is available as a binary file, which bundles all information needed to run the program. Simply download the file for your OS and execute it.

- `Windows <link>`_ (v1.0)

- `MacOS <link>`_ (v1.0)

- `Linux <link>`_ (v1.0)

Be aware that this is an experimental release of SCOUTS and, as such, is prone to bugs and errors. We kindly suggest you to `report <https://github.com/jfaccioni/scouts/issues>`_ any problems that you come across.

Installation from Github repository
-----------------------------------
SCOUTS is written in Python 3.6. If your system does not have Python 3.6 or higher, `click here to download it <https://www.python.org/downloads/>`_.

Third-party modules used by SCOUTS:

- `Numpy <http://www.numpy.org/>`_

- `Pandas <https://pandas.pydata.org/>`_

- `Pyqt5 <https://pypi.org/project/PyQt5/>`_


A full list of the third-party packages (and their dependencies) in a known working environment are listed in the `environment.yml <https://github.com/jfaccioni/scouts/environment.yml>`_ file (tested in Ubuntu 18.04).

Install with Conda
*******************
The easiest way to install SCOUTS is using a Python package manager such as `Conda <https://conda.io/docs/>`_.

- clone the repository into your local machine:

.. code-block:: none

  $ git clone https://github.com/jfaccioni/scouts

- cd into the repository:

.. code-block:: none

  $ cd scouts

- use Conda to create a new environment with the required dependencies:

.. code-block:: none

  $ conda env create --name scouts --file environment.yml

- activate the newly created environment:

.. code-block:: none

  $ conda activate scouts

- finally, run SCOUTS using your Python interpreter:

.. code-block:: none

  $ python scouts.py

Install from source
*******************
Of course, you can also download the source code and use pip to install the required packages (if you already have them in your system, you won't need to install anything).
