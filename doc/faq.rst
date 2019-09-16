FAQ
===

**I can't start SCOUTS on my computer!** ``scouts`` **does nothing!**

Please check the `installation troubleshooting section <./install.html#troubleshooting>`_.

**I can't start SCOUTS-violins on my computer!** ``scouts-violins`` **does nothing!**

Please confirm that you have installed the `necessary dependencies <./install.html#optional-scouts-violins>`_. Then check the `installation troubleshooting section <./install.html#troubleshooting>`_.

**What type of pre-processing does SCOUTS perform on my input?**

By default, SCOUTS does not perform any pre-processing prior to analysing the input data. This means that transformations like data normalization and scaling should be performed by the user prior to using SCOUTS.

SCOUTS does, however, include a simple module for gating mass cytometry and scRNA-seq samples, should the user want to do so. Refer to `How SCOUTS works <./howscoutsworks.html#gating-window>`_ for details.

**My data is stored in multiple files. How do I use SCOUTS with it?**

Ideally, you are able to merge your files into a single input file and use that to work with SCOUTS. When this is not possible, you can still use SCOUTS to run individual samples by passing one file at a time. This will not affect the output, *as long as all the cells from one sample are together in one file*. One side-effect of this method is that, in order to use the "*control*" option in the "*Consider outliers using cutoff from*" field, you need to make sure that the cells from the control sample are present in every file.

**Does the output for non-outliers exclude both top and bottom outliers?**

Yes. Even if you did not generate output files for bottom outliers, non-outliers are still considered as being "the population of cells that are not top outliers, nor bottom outliers".

**I have another question/suggestion/issue when using SCOUTS. How do I contact you?**

You can contact us through our `Github page <https://github.com/jfaccioni/scouts>`_. Check the authors section for more information. Also remember that you can use the `Github issues <https://github.com/jfaccioni/scouts/issues>`_ to post about problems or suggestions for SCOUTS.

**SCOUTS is working nicely, but can you implement X?**

Maybe! Tell us more about it on the `Github issues page <https://github.com/jfaccioni/scouts/issues>`_ :-)
