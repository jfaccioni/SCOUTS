import sys
import traceback

import cytof_analysis
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit,
                             QFileDialog)

from ui.ui_structure import Ui_OutlierAnalysis


class ColonyCounterApp(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.ui = Ui_OutlierAnalysis()
        self.ui.setupUi(self)
        self.ui.quit_main.clicked.connect(self.closeEvent)

    @pyqtSlot(name='on_back_cytof_clicked')
    @pyqtSlot(name='on_back_rnaseq_clicked')
    def goto_page_main(self):
        self.ui.pages_widget.setCurrentWidget(self.ui.page_main)

    @pyqtSlot(name='on_cytof_btn_main_clicked')
    def goto_page_cytof(self):
        self.ui.pages_widget.setCurrentWidget(self.ui.page_cytof)

    @pyqtSlot(name='on_rnaseq_btn_main_clicked')
    def goto_page_rnaseq(self):
        self.not_yet_implemented()

    @pyqtSlot(name='on_input_btn_cytof_clicked')
    def get_file(self):
        sender = self.sender()
        output_name = sender.objectName().replace('btn', 'echo')
        output = self.findChild(QLineEdit, output_name)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  "Select file", "",
                                                  "All Files (*)",
                                                  options=options)
        if filename:
            self.type_contents(output, filename)

    @pyqtSlot(name='on_output_btn_cytof_clicked')
    def get_folder(self):
        sender = self.sender()
        output_name = sender.objectName().replace('btn', 'echo')
        output = self.findChild(QLineEdit, output_name)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        foldername = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                      options=options)
        if foldername:
            self.type_contents(output, foldername)

    @staticmethod
    def type_contents(out, f):
        out.setText(f)

    @pyqtSlot(name='on_help_main_clicked')
    @pyqtSlot(name='on_help_cytof_clicked')
    @pyqtSlot(name='on_help_rnaseq_clicked')
    def get_help(self):
        self.not_yet_implemented()

    def closeEvent(self, event):
        title = 'Quit Application'
        mes = "Are you sure you want to quit?"
        reply = QMessageBox.question(self, title, mes,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit(0)

    def error_message(self, trace, e):
        title = 'An error occurred!'
        mes = "Sorry, the analysis has been stopped due to the following error:"
        fullmes = mes + '\n' + str(e) + '\n\nfull stack trace:\n\n' + str(trace)
        QMessageBox.critical(self, title, fullmes)

    def no_file_folder_found(self):
        title = 'An error occurred!'
        mes = 'No input file and/or output folder.'
        QMessageBox.critical(self, title, mes)

    def module_done(self):
        title = 'Module finished'
        mes = "The module has finished! Would you like to exit now?"
        reply = QMessageBox.question(self, title, mes,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit(0)

    def not_yet_implemented(self):
        title = 'Not Implemented yet!'
        mes = "Sorry, this module has not been implemented yet."
        QMessageBox.information(self, title, mes)

    @pyqtSlot(name='on_run_cytof_clicked')
    def run_cytof(self):
        cytof_dict = self.parse_cytof_input()
        if not cytof_dict:  # no file/folder found error message
            return  # do not perform analysis if no file/folder is found
        try:
            cytof_analysis.cytof(**cytof_dict)
        except Exception as e:
            trace = traceback.format_exc()
            self.error_message(trace, e)
        else:
            self.module_done()

    def parse_cytof_input(self):
        cytof_dict = {}
        # input and output
        try:
            input_file = str(self.ui.input_echo_cytof.text().replace('&', ''))
            output_folder = str(self.ui.input_echo_cytof.text().replace(
                '&', ''))
            assert input_file, output_folder
        except AssertionError:
            self.no_file_folder_found()
            return None
        cytof_dict['input_file'] = input_file
        cytof_dict['output_folder'] = output_folder
        # outlier generation rule
        outlier_id = self.ui.OutliersBy.checkedId()
        outlier_rule = self.ui.OutliersBy.button(outlier_id)
        cytof_dict['outliers'] = str(outlier_rule.text().replace('&', ''))
        # tuckey factor
        tuckey_id = self.ui.TuckeyFactor.checkedId()
        tuckey = self.ui.TuckeyFactor.button(tuckey_id)
        cytof_dict['tuckey'] = float(tuckey.text().replace('&', ''))
        # output settings
        if self.ui.output_text_cytof.isChecked():
            export_csv = True
        else:
            export_csv = False
        cytof_dict['export_csv'] = export_csv
        if self.ui.output_excel_cytof.isChecked():
            export_excel = True
        else:
            export_excel = False
        cytof_dict['export_excel'] = export_excel
        if self.ui.output_excel_group_cytof.isChecked():
            group_excel = True
        else:
            group_excel = False
        cytof_dict['group_excel'] = group_excel
        return cytof_dict


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ColonyCounterApp()
    gui.show()
    sys.exit(app.exec_())
