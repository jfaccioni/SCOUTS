Installation
============
SCOUTS is available as a:


* Python package from PyPI - install with ``pip``
* Conda package - install with ``conda``
* GitHub repository - download/clone the repository
* binary release (experimental)

For any installation option (other than the binary release), SCOUTS requires **Python >= 3.6** to installed in your system. To check this, open a terminal/cmd and type:

.. code-block::

   $ python3 --version

If the output is something like ``Python 3.6``\ , you're golden! Otherwise you may need to `download or upgrade Python <https://www.python.org/>`_.

For PyPI/pip or GitHub installations, we recommend using a `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_\ , instead of installing SCOUTS into your global/system-wide Python interpreter.

Install from PyPI using ``pip``
-------------------------------
To install SCOUTS, simply type in a terminal:

.. code-block::

   $ pip install scouts

then run SCOUTS by entering ``scouts`` in your terminal.

Optional: SCOUTS-violins
^^^^^^^^^^^^^^^^^^^^^^^^
If you also want to install SCOUTS-violins, type:

.. code-block::

   $ pip install scouts[violins]

then run SCOUTS-violins by entering ``scouts-violins`` in your terminal.

Install using ``conda``
-----------------------
Coming soon!

Install from the GitHub repository
----------------------------------
Download this repository into your local machine. Alternatively, clone it with ``git``\ :

.. code-block::

   $ git clone https://github.com/jfaccioni/scouts

Enter the repository's directory:

.. code-block::

   $ cd scouts

Make sure your Python interpreter (version >= 3.6) has the following packages installed:

* `numpy <http://www.numpy.org/>`_
* `pandas <https://pandas.pydata.org/>`_
* `pyside2 <https://wiki.qt.io/Qt_for_Python>`_
* `openpyxl <https://openpyxl.readthedocs.io/en/stable/>`_
* `xlrd <https://xlrd.readthedocs.io/en/latest/>`_

Run SCOUTS by typing:

.. code-block::

   $ python scouts.py

Optional: SCOUTS-violins
^^^^^^^^^^^^^^^^^^^^^^^^
If you also want to install SCOUTS-violins, make sure your Python interpreter (version >= 3.6) has the following additional packages installed:


* `matplotlib <https://matplotlib.org/>`_
* `seaborn <https://seaborn.pydata.org/>`_

Run SCOUTS-violin by typing:

.. code-block::

   $ python scouts-violins.py

Using ``pipenv`` with the GitHub repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For ``pipenv`` users, we included a ``Pipfile`` for convenience. Simply type ``pipenv install`` from the repository's directory to install SCOUTS into a virtual environment, along with the necessary third-party dependencies. This covers the installation of both SCOUTS and SCOUTS-violins.

Download binary release and run as an executable
------------------------------------------------
Download the binary release for your OS:

* `Windows <http://www.ufrgs.br/labsinal/scouts/scouts.exe>`_
* MacOS (coming soon!)
* `Linux <http://www.ufrgs.br/labsinal/scouts/scouts-linux>`_

If you choose this option, please be aware that:

* SCOUTS is a Python package. The executable has a moderately large size (~150 mb), since it has to bundle the whole Python interpreter along with it.
* this is an **experimental release of SCOUTS**\ , and as such it is not expected to support all OS configurations. If you run into any problems, please choose another installation method.
