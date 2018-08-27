import sys
import traceback

import cytof_analysis
from PyQt5.QtCore import (pyqtSlot, Qt)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit,
                             QFileDialog, QTableWidgetItem)

from ui.ui_structure import Ui_OutlierAnalysis


class ColonyCounterApp(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.ui = Ui_OutlierAnalysis()
        self.ui.setupUi(self)
        self.ui.quit_main.clicked.connect(self.close)

    @pyqtSlot(name='on_back_cytof_clicked')
    @pyqtSlot(name='on_back_rnaseq_clicked')
    def goto_page_main(self):
        self.ui.pages_widget.setCurrentWidget(self.ui.page_main)

    @pyqtSlot(name='on_cytof_btn_main_clicked')
    @pyqtSlot(name='on_saveback_btn_samples_clicked')
    def goto_page_cytof(self):
        self.ui.pages_widget.setCurrentWidget(self.ui.page_cytof)

    @pyqtSlot(name='on_rnaseq_btn_main_clicked')
    def goto_page_rnaseq(self):
        self.not_yet_implemented()

    @pyqtSlot(name='on_samples_btn_cytof_clicked')
    def goto_page_samples(self):
        self.ui.pages_widget.setCurrentWidget(self.ui.page_samples)

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

    @pyqtSlot(name='on_add_btn_samples_clicked')
    def write_to_sample_table(self):
        table = self.ui.sample_table_samples
        iscontrol = 'No'
        sample = self.ui.samplename_samples.text()
        if sample:
            for cell in range(table.rowCount()):
                item = table.item(cell, 1)
                if item.text() == sample:
                    self.same_sample()
                    return
            if self.ui.iscontrol_checkbox_samples.isChecked():
                for cell in range(table.rowCount()):
                    item = table.item(cell, 0)
                    if item.text() == 'Yes':
                        self.more_than_one_control()
                        return
                iscontrol = 'Yes'
            sample = QTableWidgetItem(sample)
            iscontrol = QTableWidgetItem(iscontrol)
            iscontrol.setFlags(Qt.ItemIsEnabled)
            row_positon = table.rowCount()
            table.insertRow(row_positon)
            table.setItem(row_positon, 1, sample)
            table.setItem(row_positon, 0, iscontrol)
            self.ui.iscontrol_checkbox_samples.setCheckState(False)
            self.ui.samplename_samples.setText('')

    @pyqtSlot(name='on_remove_btn_samples_clicked')
    def remove_from_sample_table(self):
        table = self.ui.sample_table_samples
        rows = set(index.row() for index in table.selectedIndexes())
        for index in rows:
            self.ui.sample_table_samples.removeRow(index)

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
            event.accept()
        else:
            event.ignore()

    def error_message(self, trace, e):
        title = 'An error occurred!'
        mes = "Sorry, the analysis has been stopped due to the following error:"
        fullmes = mes + '\n' + str(e) + '\n\nfull stack trace:\n\n' + str(trace)
        QMessageBox.critical(self, title, fullmes)

    def no_file_folder_found(self):
        title = 'Error: no file/folder'
        mes = 'Sorry, no input file and/or output folder was provided. Please '
        mes2 = 'add the path to the necessary file/folder.'
        QMessageBox.critical(self, title, mes + mes2)

    def same_sample(self):
        title = 'Error: sample name already in table'
        mes = "Sorry, you can't do this because this sample name is already "
        mes2 = "in the table. Please select a different name."
        QMessageBox.critical(self, title, mes + mes2)

    def more_than_one_control(self):
        title = 'Error: more than one control selected'
        mes = "Sorry, you can't do this because there is already a control "
        mes2 = "column in the table. Please remove it before adding a control."
        QMessageBox.critical(self, title, mes + mes2)

    def no_samples(self):
        title = 'Error: No samples selected'
        mes = "Sorry, the analysis cannot be performed because no sample names "
        mes2 = "were input. Please add your sample names."
        QMessageBox.critical(self, title, mes + mes2)

    @pyqtSlot(name='on_clear_btn_samples_clicked')
    def prompt_clear_data(self):
        if self.confirm_switch():
            table = self.ui.sample_table_samples
            while table.rowCount():
                self.ui.sample_table_samples.removeRow(0)
            self.goto_page_cytof()

    def confirm_switch(self):
        title = 'Confirm Action'
        mes = "Settings will be lost. Are you sure?"
        reply = QMessageBox.question(self, title, mes,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False

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
        if not cytof_dict:  # no file/folder found, no
            return  # do not perform analysis if dict is not complete
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
        input_file = str(self.ui.input_echo_cytof.text().replace('&', ''))
        output_folder = str(self.ui.output_echo_cytof.text().replace(
            '&', ''))
        if not (input_file or output_folder):
            self.no_file_folder_found()
            return
        cytof_dict['input_file'] = input_file
        cytof_dict['output_folder'] = output_folder
        # outlier generation rule
        outlier_id = self.ui.OutliersBy.checkedId()
        outlier_rule = self.ui.OutliersBy.button(outlier_id)
        cytof_dict['outliers'] = str(outlier_rule.text().replace('&', ''))
        # markers outliers rule
        markers_id = self.ui.OutliersBy.checkedId()
        markers_rule = self.ui.OutliersBy.button(markers_id)
        cytof_dict['by_marker'] = str(markers_rule.text().replace('&', ''))
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

        sample_list = []
        for tuples in self.yield_samples():
            sample_list.append(tuples)
        if not sample_list:
            self.no_samples()
            return
        cytof_dict['sample_list'] = sample_list
        return cytof_dict

    def yield_samples(self):
        table = self.ui.sample_table_samples
        for cell in range(table.rowCount()):
            sample_type = table.item(cell, 0).text()
            sample_name = table.item(cell, 1).text()
            yield sample_type, sample_name


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ColonyCounterApp()
    gui.show()
    sys.exit(app.exec_())
