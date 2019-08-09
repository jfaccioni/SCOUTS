import os
import sys
import traceback
import webbrowser

from PySide2.QtCore import Qt
from PySide2.QtGui import (QIcon, QPixmap)
from PySide2.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QDoubleSpinBox, QFileDialog, QFrame, QLabel,
                               QLineEdit, QMainWindow, QMessageBox, QPushButton, QRadioButton, QStackedWidget,
                               QTableWidget, QTableWidgetItem, QWidget)

from src import messages
from src import scouts_analysis
from src.custom_errors import ControlNotFound, EmptySampleList, PandasInputError, SampleNamingError

CUSTOM_ERRORS = (ControlNotFound, EmptySampleList, PandasInputError,
                 SampleNamingError)


class SCOUTS(QMainWindow):
    margin = {
        'left': 10,
        'top': 5,
        'right': 10,
        'bottom': 10
    }
    size = {
        'width': 600,
        'height': 600
    }
    style = {
        'title': 'QLabel {font-size:16pt; font-weight:700}',
        'subtitle': 'QLabel {font-size:12pt}',
        'info': 'QLabel {font-weight:600}',
        'credits': 'QLabel {font-style:italic}',
        'button': 'QPushButton {font-size: 10pt}'
    }

    def __init__(self):
        # ### Main Window setup
        # Inherits from QMainWindow
        super().__init__()
        # Sets values for QMainWindow
        self.setWindowTitle("SCOUTS")
        self.setWindowIcon(QIcon(os.path.join('icons', 'scouts.ico')))
        self.resize(*self.size.values())
        # Creates StackedWidget as QMainWindow's central widget
        self.stacked_pages = QStackedWidget(self)
        self.setCentralWidget(self.stacked_pages)
        # Creates Widgets for individual "pages" and adds them to the StackedWidget
        self.main_page = QWidget()
        self.samples_page = QWidget()
        self.gates_page = QWidget()
        self.pages = (self.main_page, self.samples_page, self.gates_page)
        for page in self.pages:
            self.stacked_pages.addWidget(page)
        self.stacked_pages.setMinimumSize(*self.size.values())

        # ### Sets up main_page
        # Title
        self.title = QLabel(self.main_page)
        self.title.move(self.margin['left'], self.margin['top'])
        self.title.setText('SCOUTS - Single Cell Outlier Selector')
        self.title.setStyleSheet(self.style['title'])
        self.title.adjustSize()
        # Subtitle
        self.subtitle = QLabel(self.main_page)
        self.subtitle.move(self.margin['left'], int(self.title.height() * 1.5))
        self.subtitle.setText('Please choose the settings for the analysis:')
        self.subtitle.setStyleSheet(self.style['subtitle'])
        self.subtitle.adjustSize()
        # Input button
        self.input_button = QPushButton(self.main_page)
        self.input_button.move(self.margin['left'] * 2, 20)
        self.input_button.setStyleSheet(self.style['button'])
        self.set_icon(self.input_button, 'file')
        self.input_button.setObjectName('input')
        input_button_label = 'Select input file (.xlsx or .csv) ...'
        self.input_button.setText(input_button_label)
        self.input_button.clicked.connect(self.get_path)
        # Input path box
        self.input_path = QLineEdit(self.main_page)
        self.input_path.setGeometry(30, 120, 530, 25)
        self.input_path.setObjectName('input_path')
        # Output button
        self.output_folder = QPushButton(self.main_page)
        self.output_folder.setGeometry(30, 150, 300, 25)
        self.set_icon(self.output_folder, 'folder')
        self.output_folder.setObjectName('output')
        self.output_folder.setText(' Select folder to output analysis ...')
        self.output_folder.clicked.connect(self.get_path)
        # Output path box
        self.output_path = QLineEdit(self.main_page)
        self.output_path.setGeometry(30, 180, 530, 25)
        # Input/Output section frame
        self.input_frame = QFrame(self.main_page)
        self.input_frame.setGeometry(15, 80, 560, 165)
        self.input_frame.setFrameShape(QFrame.StyledPanel)

        self.cutoff_group = QButtonGroup(self)
        self.markers_group = QButtonGroup(self)
        self.tukey_group = QButtonGroup(self)
        self.yesno_gates = QButtonGroup(self)
        self.gates_type = QButtonGroup(self)

        self.samples = QPushButton(self.main_page)
        self.samples.setGeometry(30, 210, 260, 25)
        self.set_icon(self.samples, 'settings')
        self.samples.setText(' Select sample names ...')
        self.samples.clicked.connect(self.goto_page_samples)

        self.gate = QPushButton(self.main_page)
        self.gate.setGeometry(300, 210, 260, 25)
        self.set_icon(self.gate, 'settings')
        self.gate.setText(' Gate samples ...')
        self.gate.clicked.connect(self.goto_page_gates)

        self.analysis_frame = QFrame(self.main_page)
        self.analysis_frame.setGeometry(15, 250, 560, 100)
        self.analysis_frame.setFrameShape(QFrame.StyledPanel)

        self.analysis_text = QLabel(self.main_page)
        self.analysis_text.setGeometry(30, 240, 190, 50)
        self.analysis_text.setText('Select analysis settings:')
        self.analysis_text.setStyleSheet(self.style['info'])

        self.cutoff_text = QLabel(self.main_page)
        self.cutoff_text.setGeometry(60, 262, 270, 50)
        self.cutoff_text.setText('Consider outliers using cutoff from:')

        self.cutoff_sample = QRadioButton(self.main_page)
        self.cutoff_sample.setGeometry(285, 277, 80, 25)
        self.cutoff_sample.setText('sample')
        self.cutoff_sample.setChecked(True)

        self.cutoff_control = QRadioButton(self.main_page)
        self.cutoff_control.setGeometry(395, 277, 80, 25)
        self.cutoff_control.setText('control')

        self.cutoff_both = QRadioButton(self.main_page)
        self.cutoff_both.setGeometry(505, 277, 80, 25)
        self.cutoff_both.setText('both')

        self.cutoff_group.addButton(self.cutoff_sample)
        self.cutoff_group.addButton(self.cutoff_control)
        self.cutoff_group.addButton(self.cutoff_both)

        self.markers_text = QLabel(self.main_page)
        self.markers_text.setGeometry(60, 284, 150, 50)
        self.markers_text.setText('Consider outliers for:')

        self.markers_single = QRadioButton(self.main_page)
        self.markers_single.setGeometry(285, 299, 120, 25)
        self.markers_single.setText('single marker')
        self.markers_single.setChecked(True)

        self.markers_any = QRadioButton(self.main_page)
        self.markers_any.setGeometry(395, 299, 120, 25)
        self.markers_any.setText('any marker')

        self.markers_both = QRadioButton(self.main_page)
        self.markers_both.setGeometry(505, 299, 60, 25)
        self.markers_both.setText('both')

        self.markers_group.addButton(self.markers_single)
        self.markers_group.addButton(self.markers_any)
        self.markers_group.addButton(self.markers_both)

        self.tukey_text = QLabel(self.main_page)
        self.tukey_text.setGeometry(60, 306, 150, 50)
        self.tukey_text.setText('Tukey factor:')

        self.tukey_low = QRadioButton(self.main_page)
        self.tukey_low.setGeometry(285, 321, 120, 25)
        self.tukey_low.setText('1.5')
        self.tukey_low.setChecked(True)

        self.tukey_high = QRadioButton(self.main_page)
        self.tukey_high.setGeometry(395, 321, 120, 25)
        self.tukey_high.setText('3.0')

        self.tukey_group.addButton(self.tukey_low)
        self.tukey_group.addButton(self.tukey_high)

        self.output_frame = QFrame(self.main_page)
        self.output_frame.setGeometry(15, 355, 560, 115)
        self.output_frame.setFrameShape(QFrame.StyledPanel)

        self.output_text = QLabel(self.main_page)
        self.output_text.setGeometry(30, 345, 330, 50)
        self.output_text.setText('Select output settings:')
        self.output_text.setStyleSheet(self.style['info'])

        self.output_csv = QCheckBox(self.main_page)
        self.output_csv.setGeometry(60, 380, 260, 25)
        self.output_csv.setText('Export multiple text files (.csv)')

        self.output_excel = QCheckBox(self.main_page)
        self.output_excel.setGeometry(60, 410, 310, 25)
        self.output_excel.setText('Export multiple Excel spreadsheets (.xlsx)')

        self.group_excel = QCheckBox(self.main_page)
        self.group_excel.setGeometry(60, 440, 510, 25)
        long_mes = 'Also save one Excel spreadsheet with each analysis in '
        long_mes2 = 'individual sheets'
        self.group_excel.setText(long_mes + long_mes2)
        self.group_excel.clicked.connect(self.memory_warning)

        self.run_button = QPushButton(self.main_page)
        self.run_button.setGeometry(30, 490, 400, 55)
        self.set_icon(self.run_button, 'pipe')
        self.run_button.setText(' Run !')
        self.run_button.clicked.connect(self.analyse)

        self.help_button = QPushButton(self.main_page)
        self.help_button.setGeometry(440, 490, 120, 25)
        self.set_icon(self.help_button, 'help')
        self.help_button.setText(' Help')
        self.help_button.clicked.connect(self.get_help)

        self.quit_button = QPushButton(self.main_page)
        self.quit_button.setGeometry(440, 520, 120, 25)
        self.set_icon(self.quit_button, 'quit')
        self.quit_button.setText(' Quit')
        self.quit_button.clicked.connect(self.close)

        self.credits = QLabel(self.main_page)
        self.credits.setGeometry(30, 560, 190, 50)
        self.credits.setText('Juliano Luiz Faccioni - Labsinal/UFRGS 2018')
        self.credits.setStyleSheet(self.style['credits'])
        self.credits.adjustSize()

        # Call functions to build interface
        self.set_samples_page()
        self.set_gates_page()

        self.stacked_pages.setCurrentWidget(self.main_page)

    @staticmethod
    def set_icon(widget, icon):
        i = QIcon()
        i.addPixmap(QPixmap(os.path.join('icons', f'{icon}.svg')))
        widget.setIcon(i)

    @staticmethod
    def get_help():
        webbrowser.open('https://scouts.readthedocs.io/en/master/')

    def set_samples_page(self):
        self.samples_title = QLabel(self.samples_page)
        self.samples_title.setGeometry(20, 10, 520, 60)
        self.samples_title.setText('Select samples')
        self.samples_title.setStyleSheet(self.style['title'])
        self.samples_title.adjustSize()

        self.samples_subtitle = QLabel(self.samples_page)
        self.samples_subtitle.setGeometry(25, 60, 300, 50)
        sub_label = ('Please insert your sample names (e.g. Control, Drug_01, '
                     'Treatment_x ...)\nSCOUTS locates the exact string as '
                     'part of the names on the first column of your data.')
        self.samples_subtitle.setText(sub_label)
        self.samples_subtitle.setStyleSheet(self.style['subtitle'])
        self.samples_subtitle.adjustSize()

        self.samplename = QLineEdit(self.samples_page)
        self.samplename.setGeometry(20, 110, 300, 25)
        self.samplename.setPlaceholderText('Insert sample name  ...')

        self.iscontrol = QCheckBox(self.samples_page)
        self.iscontrol.setGeometry(20, 140, 230, 25)
        self.iscontrol.setText('This is my control sample')

        self.add_row = QPushButton(self.samples_page)
        self.add_row.setGeometry(330, 110, 250, 25)
        self.set_icon(self.add_row, 'ok')
        self.add_row.setText(' Add sample to list')
        self.add_row.clicked.connect(self.write_to_sample_table)

        self.remove_row = QPushButton(self.samples_page)
        self.remove_row.setGeometry(330, 140, 250, 25)
        self.set_icon(self.remove_row, 'back')
        self.remove_row.setText(' Remove row from sample list')
        self.remove_row.clicked.connect(self.write_to_sample_table)

        self.sample_table = QTableWidget(self.samples_page)
        self.sample_table.setGeometry(20, 180, 560, 290)
        self.sample_table.setColumnCount(2)
        n, m = QTableWidgetItem('Control?'), QTableWidgetItem('Sample name')
        self.sample_table.setHorizontalHeaderItem(0, n)
        self.sample_table.setHorizontalHeaderItem(1, m)
        head = self.sample_table.horizontalHeader()
        head.setDefaultSectionSize(100)
        head.setMinimumSectionSize(100)
        head.setStretchLastSection(True)

        self.clear_samples = QPushButton(self.samples_page)
        self.clear_samples.setGeometry(430, 480, 150, 40)
        self.set_icon(self.clear_samples, 'clear')
        self.clear_samples.setText(' Clear table')
        self.clear_samples.clicked.connect(self.prompt_clear_data)

        self.save_samples = QPushButton(self.samples_page)
        self.save_samples.setGeometry(430, 530, 150, 40)
        self.set_icon(self.save_samples, 'ok')
        self.save_samples.setText(' Save samples')
        self.save_samples.clicked.connect(self.goto_page_analysis)

    def set_gates_page(self):
        self.gates_title = QLabel(self.gates_page)
        self.gates_title.setGeometry(20, 10, 520, 60)
        self.gates_title.setText('Select gate options')
        self.gates_title.setStyleSheet(self.style['title'])
        self.gates_title.adjustSize()

        self.gate_frame = QFrame(self.gates_page)
        self.gate_frame.setGeometry(15, 140, 560, 225)
        self.gate_frame.setFrameShape(QFrame.StyledPanel)

        self.no_gates = QRadioButton(self.gates_page)
        self.no_gates.setGeometry(30, 150, 220, 25)
        self.no_gates.setObjectName('no')
        self.no_gates.setText("Don't gate samples")
        self.no_gates.setChecked(True)
        self.no_gates.clicked.connect(self.activate_gate)

        self.yes_gates = QRadioButton(self.gates_page)
        self.yes_gates.setGeometry(30, 200, 120, 25)
        self.yes_gates.setObjectName('yes')
        self.yes_gates.setText('Gate samples')
        self.yes_gates.clicked.connect(self.activate_gate)

        self.yesno_gates.addButton(self.no_gates)
        self.yesno_gates.addButton(self.yes_gates)

        self.gates_cytof = QRadioButton(self.gates_page)
        self.gates_cytof.setGeometry(40, 230, 120, 25)
        m = 'Mass cytometry - exclude cells with '
        m2 = 'average row expression lower than: '
        self.gates_cytof.setText(m + m2)
        self.gates_cytof.setObjectName('cytof')
        self.gates_cytof.setChecked(True)
        self.gates_cytof.setEnabled(False)
        self.gates_cytof.adjustSize()
        self.gates_cytof.clicked.connect(self.switch_gate)

        self.gates_rna = QRadioButton(self.gates_page)
        self.gates_rna.setGeometry(40, 260, 120, 25)
        m = 'scRNA-seq - exclude "zero" values when calculating cutoff'
        self.gates_rna.setText(m)
        self.gates_rna.setObjectName('rna')
        self.gates_rna.setEnabled(False)
        self.gates_rna.adjustSize()
        self.gates_rna.clicked.connect(self.switch_gate)

        self.gates_type.addButton(self.gates_rna)
        self.gates_type.addButton(self.gates_cytof)

        self.not_outliers = QCheckBox(self.gates_page)
        self.not_outliers.setGeometry(40, 290, 230, 25)
        m = 'Also generate results for non-outliers'
        self.not_outliers.setText(m)
        self.not_outliers.setEnabled(False)
        self.not_outliers.adjustSize()

        self.bottom_outliers = QCheckBox(self.gates_page)
        self.bottom_outliers.setGeometry(40, 320, 230, 25)
        m = 'Also generate results for low outliers'
        self.bottom_outliers.setText(m)
        self.bottom_outliers.setEnabled(False)
        self.bottom_outliers.adjustSize()

        self.gates_cytof_value = QDoubleSpinBox(self.gates_page)
        self.gates_cytof_value.setGeometry(502, 228, 120, 25)
        self.gates_cytof_value.setMinimum(0)
        self.gates_cytof_value.setMaximum(1)
        self.gates_cytof_value.setValue(0.1)
        self.gates_cytof_value.setSingleStep(0.05)
        self.gates_cytof_value.setEnabled(False)
        self.gates_cytof_value.adjustSize()

        self.save_gates = QPushButton(self.gates_page)
        self.save_gates.setGeometry(430, 530, 150, 40)
        self.set_icon(self.save_gates, 'ok')
        self.save_gates.setText(' Save gate options')
        self.save_gates.clicked.connect(self.goto_page_analysis)

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

    def goto_page_analysis(self):
        self.page.setCurrentWidget(self.analysis_page)

    def goto_page_samples(self):
        self.page.setCurrentWidget(self.samples_page)

    def goto_page_gates(self):
        self.page.setCurrentWidget(self.gates_page)

    def get_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        name = self.sender().objectName()
        query = ''
        echo = ''
        if name == 'input':
            echo = self.input_path
            query, _ = QFileDialog.getOpenFileName(self,
                                                   "Select file", "",
                                                   "All Files (*)",
                                                   options=options)
        elif name == 'output':
            echo = self.output_path
            query = QFileDialog.getExistingDirectory(self,
                                                     "Select Directory",
                                                     options=options)
        if query:
            echo.setText(query)

    def memory_warning(self):
        if self.sender().isChecked():
            messages.memory_warning(self)

    def write_to_sample_table(self):
        table = self.sample_table
        iscontrol = 'No'
        sample = self.samplename.text()
        if sample:
            for cell in range(table.rowCount()):
                item = table.item(cell, 1)
                if item.text() == sample:
                    messages.same_sample(self)
                    return
            if self.iscontrol.isChecked():
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
            self.iscontrol.setChecked(False)
            self.samplename.setText('')

    def remove_from_sample_table(self):
        table = self.sample_table
        rows = set(index.row() for index in table.selectedIndexes())
        for index in rows:
            self.sample_table.removeRow(index)

    def prompt_clear_data(self):
        if self.confirm_switch():
            table = self.sample_table
            while table.rowCount():
                self.sample_table.removeRow(0)

    def confirm_switch(self):
        title = 'Confirm Action'
        mes = "Settings will be lost. Are you sure?"
        reply = QMessageBox.question(self, title, mes,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False

    def activate_gate(self):
        if self.sender().objectName() == 'no':
            self.gates_cytof.setEnabled(False)
            self.gates_rna.setEnabled(False)
            self.gates_cytof_value.setEnabled(False)
            self.not_outliers.setChecked(False)
            self.not_outliers.setEnabled(False)
            self.bottom_outliers.setEnabled(False)
            self.bottom_outliers.setChecked(False)
        elif self.sender().objectName() == 'yes':
            self.gates_cytof.setEnabled(True)
            if self.gates_cytof.isChecked():
                self.gates_cytof_value.setEnabled(True)
            self.gates_rna.setEnabled(True)
            self.not_outliers.setEnabled(True)
            self.bottom_outliers.setEnabled(True)

    def switch_gate(self):
        if self.sender().objectName() == 'cytof':
            self.gates_cytof_value.setEnabled(True)
        elif self.sender().objectName() == 'rna':
            self.gates_cytof_value.setEnabled(False)
            self.gates_cytof_value.setValue(0.1)

    def analyse(self):
        try:
            input_dict = self.parse_input()
            assert input_dict
            scouts_analysis.analyse(self, **input_dict)
        except Exception as e:
            if type(e) not in CUSTOM_ERRORS and type(e) != AssertionError:
                trace = traceback.format_exc()
                messages.generic_error_message(self, trace, e)
        else:
            messages.module_done(self)

    def parse_input(self):
        input_dict = {}
        # Input and output
        input_file = self.input_path.text()
        output_folder = self.output_path.text()
        if not (input_file or output_folder):
            messages.no_file_folder_found(self)
            return
        input_dict['input_file'] = input_file
        input_dict['output_folder'] = output_folder
        # Set cutoff by control or by sample rule
        cutoff_id = self.cutoff_group.checkedId()
        cutoff_rule = self.cutoff_group.button(cutoff_id)
        input_dict['cutoff_rule'] = cutoff_rule.text()
        # Outliers for each individual marker or any marker in row
        markers_id = self.markers_group.checkedId()
        markers_rule = self.markers_group.button(markers_id)
        input_dict['by_marker'] = markers_rule.text()
        # Tukey factor used for calculating cutoff
        tukey_id = self.tukey_group.checkedId()
        tukey = self.tukey_group.button(tukey_id)
        input_dict['tukey'] = float(tukey.text())
        # Output settings
        if self.output_csv.isChecked():
            export_csv = True
        else:
            export_csv = False
        input_dict['export_csv'] = export_csv
        if self.output_excel.isChecked():
            export_excel = True
        else:
            export_excel = False
        input_dict['export_excel'] = export_excel
        if self.group_excel.isChecked():
            group_excel = True
        else:
            group_excel = False
        input_dict['group_excel'] = group_excel
        # Retrieve information about sample names and which sample is control
        sample_list = []
        for tuples in self.yield_samples():
            sample_list.append(tuples)
        if not sample_list:
            messages.no_samples(self)
            return
        input_dict['sample_list'] = sample_list
        # Set gate cutoff, if any
        gate_cutoff = None
        not_outliers = False
        bottom_outliers = False
        if not self.no_gates.isChecked():
            gate_id = self.gates_type.checkedId()
            gate_option = self.gates_type.button(gate_id)
            if gate_option.objectName() == 'cytof':
                gate_cutoff = self.gates_cytof_value.value()
            elif gate_option.objectName() == 'rna':
                gate_cutoff = 'no-zero'
            if self.not_outliers.isChecked():
                not_outliers = True
            if self.bottom_outliers.isChecked():
                bottom_outliers = True
        input_dict['gate_cutoff'] = gate_cutoff
        input_dict['not_outliers'] = not_outliers
        input_dict['bottom_outliers'] = bottom_outliers
        return input_dict

    def yield_samples(self):
        table = self.sample_table
        for cell in range(table.rowCount()):
            sample_type = table.item(cell, 0).text()
            sample_name = table.item(cell, 1).text()
            yield sample_type, sample_name


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SCOUTS()
    gui.show()
    sys.exit(app.exec_())
