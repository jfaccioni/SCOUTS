import sys
import traceback
import webbrowser

from PyQt5.QtCore import (Qt, pyqtSlot)
from PyQt5.QtWidgets import (QApplication, QFileDialog, QLineEdit, QMainWindow,
                             QMessageBox, QTableWidgetItem)

import cytof_analysis
from ui import messages
from ui.custom_errors import (ControlNotFound, EmptySampleList,
                              PandasInputError, SampleNamingError)
from ui.ui_structure import Ui_OutlierAnalysis

CUSTOM_ERRORS = (ControlNotFound, EmptySampleList, PandasInputError,
                 SampleNamingError)


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
        messages.not_yet_implemented(self)

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
                    messages.same_sample(self)
                    return
            if self.ui.iscontrol_checkbox_samples.isChecked():
                for cell in range(table.rowCount()):
                    item = table.item(cell, 0)
                    if item.text() == 'Yes':
                        messages.more_than_one_control(self)
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

    @pyqtSlot(name='on_output_excel_group_cytof_clicked')
    def memory_warning(self):
        if self.sender().isChecked():
            messages.memory_warning(self)

    @pyqtSlot(name='on_run_cytof_clicked')
    def run_cytof(self):
        try:
            cytof_dict = self.parse_cytof_input()
            assert cytof_dict
            cytof_analysis.cytof(self, **cytof_dict)
        except Exception as e:
            if type(e) not in CUSTOM_ERRORS and type(e) != AssertionError:
                trace = traceback.format_exc()
                messages.generic_error_message(self, trace, e)
        else:
            messages.module_done(self)

    def parse_cytof_input(self):
        cytof_dict = {}
        # input and output
        input_file = str(self.ui.input_echo_cytof.text().replace('&', ''))
        output_folder = str(self.ui.output_echo_cytof.text().replace('&', ''))
        if not (input_file or output_folder):
            messages.no_file_folder_found(self)
            return
        cytof_dict['input_file'] = input_file
        cytof_dict['output_folder'] = output_folder
        # set cutoff by control or by sample rule
        outlier_id = self.ui.OutliersBy.checkedId()
        outlier_rule = self.ui.OutliersBy.button(outlier_id)
        cytof_dict['outliers'] = str(outlier_rule.text().replace('&', ''))
        # outliers for each individual marker or any marker in row
        markers_id = self.ui.MarkersOutliers.checkedId()
        markers_rule = self.ui.MarkersOutliers.button(markers_id)
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
        # retrieve information about sample names and which sample is control
        sample_list = []
        for tuples in self.yield_samples():
            sample_list.append(tuples)
        if not sample_list:
            messages.no_samples(self)
            return
        cytof_dict['sample_list'] = sample_list
        return cytof_dict

    def yield_samples(self):
        table = self.ui.sample_table_samples
        for cell in range(table.rowCount()):
            sample_type = table.item(cell, 0).text()
            sample_name = table.item(cell, 1).text()
            yield sample_type, sample_name

    @pyqtSlot(name='on_help_main_clicked')
    @pyqtSlot(name='on_help_cytof_clicked')
    @pyqtSlot(name='on_help_rnaseq_clicked')
    def get_help(self):
        webbrowser.open('http://www.google.com')

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ColonyCounterApp()
    gui.show()
    sys.exit(app.exec_())
