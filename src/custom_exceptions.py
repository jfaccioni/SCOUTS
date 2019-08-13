import traceback

from PySide2.QtWidgets import QMessageBox


class GenericError(Exception):
    def __init__(self, widget):
        Exception.__init__(self)
        trace = traceback.format_exc()
        self.generic_error_message(widget, trace)

    def generic_error_message(self, widget, trace):
        title = 'An error occurred!'
        mes = "Sorry, the analysis has been stopped due to the following error:"
        fullmes = mes + '\n' + str(self) + '\n\nfull stack trace:\n\n' + str(trace)
        QMessageBox.critical(widget, title, fullmes)


class NoIOPathError(Exception):
    def __init__(self, widget):
        Exception.__init__(self)
        self.no_file_folder_found(widget)

    @staticmethod
    def no_file_folder_found(widget):
        title = 'Error: no file/folder'
        mes = ("Sorry, no input file and/or output folder was provided. "
               "Please add the path to the necessary file/folder.")
        QMessageBox.critical(widget, title, mes)


class EmptySampleListError(Exception):
    def __init__(self, widget):
        Exception.__init__(self)
        self.empty_sample_list(widget)

    @staticmethod
    def empty_sample_list(widget):
        title = 'Error: No control sample'
        mes = ("Sorry, your samples do not include a control. Please make sure to "
               "tag one of the samples as a control.")
        QMessageBox.critical(widget, title, mes)


class PandasInputError(Exception):
    def __init__(self, widget):
        Exception.__init__(self)
        self.pandas_input_error(widget)

    @staticmethod
    def pandas_input_error(widget):
        title = 'Error: unexpected input file'
        mes = ("Sorry, the input file could not be read. Please make sure that "
               "the data is save in a valid format ( supported formats are: "
               ".csv, .xlsx).")
        QMessageBox.critical(widget, title, mes)


class SampleNamingError(Exception):
    def __init__(self, widget):
        Exception.__init__(self)
        self.sample_naming_error(widget)

    @staticmethod
    def sample_naming_error(widget):
        title = 'Error: sample names not in input file'
        mes = ("Sorry, your sample names were not found in the input file. Please "
               "make sure that the names were typed correctly (case-sensitive).")
        QMessageBox.critical(widget, title, mes + mes2)


class NoSampleError(Exception):
    def __init__(self, widget):
        Exception.__init__(self)
        self.no_samples(widget)

    @staticmethod
    def no_samples(widget):
        title = "Error: No samples selected"
        mes = ("Sorry, the analysis cannot be performed because no sample names were input."
               "Please add your sample names.")
        QMessageBox.critical(widget, title, mes + mes2)
