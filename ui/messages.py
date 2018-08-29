from PyQt5.QtWidgets import QMessageBox


def module_done(widget):
    title = 'Analysis finished!'
    mes = "Your analysis has finished. No errors were reported."
    QMessageBox.information(widget, title, mes)


def memory_warning(widget):
    title = 'Warning!'
    mes = "Depending on your dataset, this option can consume a LOT of memory. "
    mes2 = "Please make sure that your computer can handle it!"
    QMessageBox.critical(widget, title, mes + mes2)


def generic_error_message(widget, trace, e):
    title = 'An error occurred!'
    mes = "Sorry, the analysis has been stopped due to the following error:"
    fullmes = mes + '\n' + str(e) + '\n\nfull stack trace:\n\n' + str(trace)
    QMessageBox.critical(widget, title, fullmes)


def empty_sample_list(widget):
    title = 'Error: No control sample'
    mes = "Sorry, your samples do not include a control. Please make sure to "
    mes2 = "tag one of the samples as a control."
    QMessageBox.critical(widget, title, mes + mes2)


def control_not_found(widget):
    title = 'Error: No control sample'
    mes = "Sorry, your samples do not include a control. Please make sure to "
    mes2 = "tag one of the samples as a control."
    QMessageBox.critical(widget, title, mes + mes2)


def pandas_input_error(widget):
    title = 'Error: unexpected input file'
    mes = "Sorry, the input file could not be read. Please make sure that "
    mes2 = "the data is save in a valid format ( supported formats are: "
    mes3 = ".csv, .xlsx)."
    QMessageBox.critical(widget, title, mes + mes2 + mes3)


def sample_naming_error(widget):
    title = 'Error: sample names not in input file'
    mes = "Sorry, your sample names were not found in the input file. Please "
    mes2 = "make sure that the names were typed correctly (case-sensitive)."
    QMessageBox.critical(widget, title, mes + mes2)


def no_file_folder_found(widget):
    title = 'Error: no file/folder'
    mes = 'Sorry, no input file and/or output folder was provided. Please '
    mes2 = 'add the path to the necessary file/folder.'
    QMessageBox.critical(widget, title, mes + mes2)


def same_sample(widget):
    title = 'Error: sample name already in table'
    mes = "Sorry, you can't do this because this sample name is already "
    mes2 = "in the table. Please select a different name."
    QMessageBox.critical(widget, title, mes + mes2)


def more_than_one_control(widget):
    title = 'Error: more than one control selected'
    mes = "Sorry, you can't do this because there is already a control "
    mes2 = "column in the table. Please remove it before adding a control."
    QMessageBox.critical(widget, title, mes + mes2)


def no_samples(widget):
    title = 'Error: No samples selected'
    mes = "Sorry, the analysis cannot be performed because no sample names "
    mes2 = "were input. Please add your sample names."
    QMessageBox.critical(widget, title, mes + mes2)


def not_yet_implemented(widget):
    title = 'Not Implemented yet!'
    mes = "Sorry, this functionality has not been implemented yet."
    QMessageBox.information(widget, title, mes)