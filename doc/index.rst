.. SCOUTS documentation master file, created by
   sphinx-quickstart on Tue Sep  4 08:54:11 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**SCOUTS**
==========

Single Cell OUTlier Selector
----------------------------

**SCOUTS** is a tool that quickly finds outliers in your single-cell data, generating information about your population organized by targeted molecules.

Why SCOUTS?
***********

SCOUTS takes your single-cell input and generates output files containing only outliers. The method used by SCOUTS to subset the population and find the outliers is customizable through the program's interface.

Many single cell analysis pipelines require some level of programming knowledge in order to be used. While some great tools for languages like R, Python and Julia have been developed, the entry-level barrier of programming is still intimidating for many scientists starting on the field of singe-cell analysis. With this in mind, we developed SCOUTS to simplify this process. Through a desktop application, the user is able to select the parameters for the outlier selection, and leave the hard work of programatically subsetting the data to SCOUTS.

Of course, being a open-source project distributed under the MIT license, those with a more robust programming background are welcome to read the source code of SCOUTS and adapt it to their specific needs.

Usage & documentation
*********************

.. toctree::
   :maxdepth: 2

   Installation <install>
   Quickstart guide <start>
   How SCOUTS works <work>
   FAQ <faq>

* :ref:`search`
