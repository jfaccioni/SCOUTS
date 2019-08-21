from PySide2.QtWidgets import QMessageBox


class CustomException(Exception):
    def __init__(self, widget, title, message):
        super().__init__()
        QMessageBox.critical(widget, title, message)


class NoIOPathError(CustomException):
    def __init__(self, widget):
        title = 'Error: no file/folder'
        message = ("Sorry, no input file and/or output folder was provided. "
                   "Please add the path to the necessary file/folder.")
        super().__init__(widget, title, message)


class EmptySampleListError(CustomException):
    def __init__(self, widget):
        title = 'Error: No control sample'
        message = ("Sorry, your samples do not include a control. Please make sure to "
                   "tag one of the samples as a control.")
        super().__init__(widget, title, message)


class PandasInputError(CustomException):
    def __init__(self, widget):
        title = 'Error: unexpected input file'
        message = ("Sorry, the input file could not be read. Please make sure that "
                   "the data is save in a valid format (supported formats are: "
                   ".csv, .xlsx).")
        super().__init__(widget, title, message)


class SampleNamingError(CustomException):
    def __init__(self, widget):
        title = 'Error: sample names not in input file'
        message = ("Sorry, your sample names were not found in the input file. Please "
                   "make sure that the names were typed correctly (case-sensitive).")
        super().__init__(widget, title, message)


class NoSampleError(CustomException):
    def __init__(self, widget):
        title = "Error: No samples selected"
        message = ("Sorry, the analysis cannot be performed because no sample names were input. "
                   "Please add your sample names.")
        super().__init__(widget, title, message)


class NoReferenceError(CustomException):
    def __init__(self, widget):
        title = "Error: No samples selected"
        message = ("Sorry, no reference sample was found on the sample list, but analysis was set to "
                   "reference. Please add a reference sample, or change the rule for cutoff calculation.")
        super().__init__(widget, title, message)
