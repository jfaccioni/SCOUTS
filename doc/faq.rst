FAQ
===

**What type of pre-processing does SCOUTS perform on my input?**

By default, SCOUTS does not perform any pre-processing prior to analysing the input data. This means that transformations like data normalization and scaling should be performed by the user prior to using SCOUTS.

SCOUTS does, however, include a simple module for gating mass cytometry and scRNA-seq samples, should the user want to do so. Refer to `How SCOUTS works <./work.html>`_ for details.

**My data is stored in multiple files. How do I use SCOUTS with it?**

Ideally, you can merge your files into a single input file and use that to work with SCOUTS. When this is not possible, you can still use SCOUTS to analyse individual samples by passing one file at a time. This will not affect the output, *as long as all the cells from one sample are together in one file*. One side-effect of this method is that, in order to use the "*control*" option in the "*Consider outliers using cutoff from*" field, you need to make sure that the cells from the control sample are present in every file.

**I do not have a control sample. Can I run SCOUTS without explicitly informing a control sample?**

In order to run SCOUTS, you **need** to indicate one control sample; if you do not have a control sample, any sample will do. Simply add any sample as a control sample to the sample list. Don't forget to check the "*samples*" option in the "*Consider outliers using cutoff from*" field.

**Does the output for non-outliers exclude both top and bottom outliers?**

No. Output for non-outliers is generated on a per-condition basis, which means that two different files are generated for non-outliers: one excluding the top outliers and one excluding the bottom outliers (given you chose this option on the gate page).

**I have another question/suggestion/issue when using SCOUTS. How do I contact you?**

You can contact us through our `Github page <https://github.com/jfaccioni/scouts>`_. Check the authors section for more information. Also remember that you can use the `Github issues <https://github.com/jfaccioni/scouts/issues>`_ to post about problems or suggestions for SCOUTS.

**SCOUTS is working nicely, but can you implement X Y Z?**

Maybe! Tell us more about it on the `Github issues page <https://github.com/jfaccioni/scouts/issues>`_ :-)
