import sys
from PyQt5.QtWidgets import QMessageBox


def error_message(widget, trace, e):
    title = 'An error occurred!'
    mes = "Sorry, the analysis has been stopped due to the following error:"
    fullmes = mes + '\n' + str(e) + '\n\nfull stack trace:\n\n' + str(trace)
    QMessageBox.critical(widget, title, fullmes)


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


def module_done(widget):
    title = 'Module finished'
    mes = "The module has finished! Would you like to exit now?"
    reply = QMessageBox.question(widget, title, mes,
                                 QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.No)
    if reply == QMessageBox.Yes:
        sys.exit(0)


def not_yet_implemented(widget):
    title = 'Not Implemented yet!'
    mes = "Sorry, this module has not been implemented yet."
    QMessageBox.information(widget, title, mes)
