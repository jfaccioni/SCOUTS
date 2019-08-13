from __future__ import annotations

import os
import sys
import webbrowser
from typing import Dict, Generator, Tuple, TYPE_CHECKING

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame,
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
                               QRadioButton, QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from src.analysis import analyse
from src.custom_exceptions import (EmptySampleListError, GenericError, NoIOPathError, NoSampleError, PandasInputError,
                                   SampleNamingError)

CUSTOM_ERRORS = (EmptySampleListError, NoIOPathError, NoSampleError, PandasInputError, SampleNamingError)
if TYPE_CHECKING:
    from PySide2.QtCore import QEvent


class SCOUTS(QMainWindow):
    margin = {
        'left': 10,
        'top': 5,
        'right': 10,
        'bottom': 10
    }
    size = {
        'width': 480,
        'height': 640
    }
    style = {
        'title': 'QLabel {font-size:18pt; font-weight:700}',
        'subtitle': 'QLabel {font-size:12pt}',
        'header': 'QLabel {font-weight:600}',
        'button': 'QPushButton {font-size: 10pt}',
        'label': 'QLabel {font-size: 10pt}',
        'bold-label': 'QLabel {font-size: 10pt; font-weight:500}',
        'radio button': 'QRadioButton {font-size: 10pt}',
        'checkbox': 'QCheckBox {font-size: 10pt}',
        'line edit': 'QLineEdit {font-size: 10pt}',
        'credits': 'QLabel {font-style:italic; font-size:10pt}',
    }

    def __init__(self) -> None:
        # ###
        # ### Main Window setup
        # ###

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
        # ## Sets widget at program startup
        self.stacked_pages.setCurrentWidget(self.main_page)

        # ###
        # ### MAIN PAGE
        # ###

        # Title section
        # Title
        self.title = QLabel(self.main_page)
        self.title.move(self.margin['left'], self.margin['top'])
        self.title.setText('SCOUTS - Single Cell Outlier Selector')
        self.title.setStyleSheet(self.style['title'])
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # ## Input section
        # Input header
        self.input_header = QLabel(self.main_page)
        self.input_header.move(self.margin['left'], self.widget_vposition(self.title) + 5)
        self.input_header.setText('Input settings')
        self.input_header.setStyleSheet(self.style['header'])
        self.input_header.adjustSize()
        # Input frame
        self.input_frame = QFrame(self.main_page)
        self.input_frame.setGeometry(self.margin['left'],
                                     self.widget_vposition(self.input_header) + 5, self.stretch(), 105)
        self.input_frame.setFrameShape(QFrame.StyledPanel)
        self.input_frame.setLayout(QFormLayout())
        # Input button
        self.input_button = QPushButton(self.main_page)
        self.input_button.setStyleSheet(self.style['button'])
        self.set_icon(self.input_button, 'file')
        self.input_button.setObjectName('input')
        self.input_button.setText(' Select input file (.xlsx or .csv)')
        self.input_button.clicked.connect(self.get_path)
        # Input path box
        self.input_path = QLineEdit(self.main_page)
        self.input_path.setObjectName('input_path')
        self.input_path.setStyleSheet(self.style['line edit'])
        # Go to sample naming page
        self.samples_button = QPushButton(self.main_page)
        self.samples_button.setStyleSheet(self.style['button'])
        self.set_icon(self.samples_button, 'settings')
        self.samples_button.setText(' Select sample names...')
        self.samples_button.clicked.connect(self.goto_samples_page)
        # Go to gating page
        self.gates_button = QPushButton(self.main_page)
        self.gates_button.setStyleSheet(self.style['button'])
        self.set_icon(self.gates_button, 'settings')
        self.gates_button.setText(' Gating && outlier options...')
        self.gates_button.clicked.connect(self.goto_gates_page)
        # Add widgets above to input frame Layout
        self.input_frame.layout().addRow(self.input_button, self.input_path)
        self.input_frame.layout().addRow(self.samples_button)
        self.input_frame.layout().addRow(self.gates_button)

        # ## Analysis section
        # Analysis header
        self.analysis_header = QLabel(self.main_page)
        self.analysis_header.move(self.margin['left'], self.widget_vposition(self.input_frame) + 15)
        self.analysis_header.setText('Analysis settings')
        self.analysis_header.setStyleSheet(self.style['header'])
        self.analysis_header.adjustSize()
        # Analysis frame
        self.analysis_frame = QFrame(self.main_page)
        self.analysis_frame.setGeometry(self.margin['left'],
                                        self.widget_vposition(self.analysis_header) + 5, self.stretch(), 155)
        self.analysis_frame.setFrameShape(QFrame.StyledPanel)
        self.analysis_frame.setLayout(QVBoxLayout())
        # Cutoff text
        self.cutoff_text = QLabel(self.main_page)
        self.cutoff_text.setText('Consider outliers using cutoff from:')
        self.cutoff_text.setStyleSheet(self.style['bold-label'])
        # Cutoff button group
        self.cutoff_group = QButtonGroup(self)
        # Cutoff by sample
        self.cutoff_sample = QRadioButton(self.main_page)
        self.cutoff_sample.setText('sample')
        self.cutoff_sample.setStyleSheet(self.style['radio button'])
        self.cutoff_sample.setChecked(True)
        self.cutoff_group.addButton(self.cutoff_sample)
        # Cutoff by reference
        self.cutoff_reference = QRadioButton(self.main_page)
        self.cutoff_reference.setText('reference')
        self.cutoff_reference.setStyleSheet(self.style['radio button'])
        self.cutoff_group.addButton(self.cutoff_reference)
        # Both cutoffs
        self.cutoff_both = QRadioButton(self.main_page)
        self.cutoff_both.setText('both')
        self.cutoff_both.setStyleSheet(self.style['radio button'])
        self.cutoff_group.addButton(self.cutoff_both)
        # Markers text
        self.markers_text = QLabel(self.main_page)
        self.markers_text.setStyleSheet(self.style['bold-label'])
        self.markers_text.setText('Consider outliers for:')
        # Markers button group
        self.markers_group = QButtonGroup(self)
        # Single marker
        self.single_marker = QRadioButton(self.main_page)
        self.single_marker.setText('single marker')
        self.single_marker.setStyleSheet(self.style['radio button'])
        self.single_marker.setChecked(True)
        self.markers_group.addButton(self.single_marker)
        # Any marker
        self.any_marker = QRadioButton(self.main_page)
        self.any_marker.setText('any marker')
        self.any_marker.setStyleSheet(self.style['radio button'])
        self.markers_group.addButton(self.any_marker)
        # Both methods
        self.both_methods = QRadioButton(self.main_page)
        self.both_methods.setText('both methods')
        self.both_methods.setStyleSheet(self.style['radio button'])
        self.markers_group.addButton(self.both_methods)
        # Tukey text
        self.tukey_text = QLabel(self.main_page)
        self.tukey_text.setStyleSheet(self.style['bold-label'])
        # Tukey button group
        self.tukey_text.setText('Tukey factor:')
        self.tukey_group = QButtonGroup(self)
        # Low Tukey value
        self.tukey_low = QRadioButton(self.main_page)
        self.tukey_low.setText('1.5')
        self.tukey_low.setStyleSheet(self.style['radio button'])
        self.tukey_low.setChecked(True)
        self.tukey_group.addButton(self.tukey_low)
        # High Tukey value
        self.tukey_high = QRadioButton(self.main_page)
        self.tukey_high.setText('3.0')
        self.tukey_high.setStyleSheet(self.style['radio button'])
        self.tukey_group.addButton(self.tukey_high)
        # Add widgets above to analysis frame layout
        self.analysis_frame.layout().addWidget(self.cutoff_text)
        self.cutoff_buttons = QHBoxLayout()
        for button in self.cutoff_group.buttons():
            self.cutoff_buttons.addWidget(button)
        self.analysis_frame.layout().addLayout(self.cutoff_buttons)
        self.analysis_frame.layout().addWidget(self.markers_text)
        self.markers_buttons = QHBoxLayout()
        for button in self.markers_group.buttons():
            self.markers_buttons.addWidget(button)
        self.analysis_frame.layout().addLayout(self.markers_buttons)
        self.analysis_frame.layout().addWidget(self.tukey_text)
        self.tukey_buttons = QHBoxLayout()
        for button in self.tukey_group.buttons():
            self.tukey_buttons.addWidget(button)
        self.tukey_buttons.addWidget(QLabel())  # aligns row with 2 buttons
        self.analysis_frame.layout().addLayout(self.tukey_buttons)

        # ## Output section
        # Output header
        self.output_header = QLabel(self.main_page)
        self.output_header.move(self.margin['left'], self.widget_vposition(self.analysis_frame) + 15)
        self.output_header.setText('Output settings')
        self.output_header.setStyleSheet(self.style['header'])
        self.output_header.adjustSize()
        # Output frame
        self.output_frame = QFrame(self.main_page)
        self.output_frame.setGeometry(self.margin['left'],
                                      self.widget_vposition(self.output_header) + 5, self.stretch(), 140)
        self.output_frame.setFrameShape(QFrame.StyledPanel)
        self.output_frame.setLayout(QFormLayout())
        # Output button
        self.output_button = QPushButton(self.main_page)
        self.output_button.setStyleSheet(self.style['button'])
        self.set_icon(self.output_button, 'folder')
        self.output_button.setObjectName('output')
        self.output_button.setText(' Select output folder')
        self.output_button.clicked.connect(self.get_path)
        # Output path box
        self.output_path = QLineEdit(self.main_page)
        self.output_path.setStyleSheet(self.style['line edit'])
        # Generate CSV checkbox
        self.output_csv = QCheckBox(self.main_page)
        self.output_csv.setText('Export multiple text files (.csv)')
        self.output_csv.setStyleSheet(self.style['checkbox'])
        # Generate XLSX checkbox
        self.output_excel = QCheckBox(self.main_page)
        self.output_excel.setText('Export multiple Excel spreadsheets (.xlsx)')
        self.output_excel.setStyleSheet(self.style['checkbox'])
        # Generate single, large XLSX checkbox
        self.single_excel = QCheckBox(self.main_page)
        self.single_excel.setText('Also save one Excel spreadsheet with each analysis in individual sheets')
        self.single_excel.setStyleSheet(self.style['checkbox'])
        self.single_excel.clicked.connect(self.memory_warning)
        # Add widgets above to output frame layout
        self.output_frame.layout().addRow(self.output_button, self.output_path)
        self.output_frame.layout().addRow(self.output_csv)
        self.output_frame.layout().addRow(self.output_excel)
        self.output_frame.layout().addRow(self.single_excel)

        # ## Run & help-quit section
        # Run button (stand-alone)
        self.run_button = QPushButton(self.main_page)
        self.run_button.setGeometry(self.margin['left'],
                                    self.widget_vposition(self.output_frame) + 5, self.stretch(), 30)
        self.set_icon(self.run_button, 'pipe')
        self.run_button.setText(' Run!')
        self.run_button.setText(' Run!')
        self.run_button.clicked.connect(self.analyse)
        # Help-quit frame (invisible)
        self.helpquit_frame = QFrame(self.main_page)
        self.helpquit_frame.setGeometry(self.margin['left'],
                                        self.widget_vposition(self.run_button) + 5, self.stretch(), 30)
        helpquit_layout = QHBoxLayout()
        helpquit_layout.setMargin(0)
        self.helpquit_frame.setLayout(helpquit_layout)
        # Help button
        self.help_button = QPushButton(self.main_page)
        self.set_icon(self.help_button, 'help')
        self.help_button.setText(' Help')
        self.help_button.clicked.connect(self.get_help)
        # Quit button
        self.quit_button = QPushButton(self.main_page)
        self.set_icon(self.quit_button, 'quit')
        self.quit_button.setText(' Quit')
        self.quit_button.clicked.connect(self.close)
        # Add widgets above to help-quit layout
        self.helpquit_frame.layout().addWidget(self.help_button)
        self.helpquit_frame.layout().addWidget(self.quit_button)

        # ###
        # ### SAMPLES PAGE
        # ###

        # ## Title section
        # Title
        self.samples_title = QLabel(self.samples_page)
        self.samples_title.move(self.margin['left'], self.margin['top'])
        self.samples_title.setText('Sample names')
        self.samples_title.setStyleSheet(self.style['title'])
        self.samples_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # Subtitle
        self.samples_subtitle = QLabel(self.samples_page)
        self.samples_subtitle.move(self.margin['left'], self.widget_vposition(self.samples_title) + 5)
        string = ('Please insert your sample names\ne.g. Control, Drug-01, '
                  'Treatment_X ...\n\nSCOUTS locates the exact string as '
                  'part of\nthe names on the first column of your data.')
        self.samples_subtitle.setText(string)
        self.samples_subtitle.setStyleSheet(self.style['bold-label'])
        self.samples_subtitle.adjustSize()

        # ## Sample addition section
        # Sample addition frame
        self.samples_frame = QFrame(self.samples_page)
        self.samples_frame.setGeometry(self.margin['left'],
                                       self.widget_vposition(self.samples_subtitle) + 5, self.stretch(), 80)
        self.samples_frame.setFrameShape(QFrame.StyledPanel)
        self.samples_frame.setLayout(QFormLayout())
        # Sample name box
        self.sample_name = QLineEdit(self.samples_page)
        self.sample_name.setStyleSheet(self.style['line edit'])
        self.sample_name.resize(400, self.sample_name.height())
        self.sample_name.setPlaceholderText('Insert sample name  ...')
        # Reference check
        self.is_reference = QCheckBox(self.samples_page)
        self.is_reference.setText('This is my reference sample')
        self.is_reference.setStyleSheet(self.style['checkbox'])
        # Add sample to table
        self.add_sample_button = QPushButton(self.samples_page)
        self.set_icon(self.add_sample_button, 'ok')
        self.add_sample_button.setText(' Add sample to table')
        self.add_sample_button.setStyleSheet(self.style['button'])
        self.add_sample_button.clicked.connect(self.write_to_sample_table)
        # Remove sample from table
        self.remove_sample_button = QPushButton(self.samples_page)
        self.set_icon(self.remove_sample_button, 'back')
        self.remove_sample_button.setText(' Remove sample from table')
        self.remove_sample_button.setStyleSheet(self.style['button'])
        self.remove_sample_button.clicked.connect(self.remove_from_sample_table)
        # Add widgets above to sample addition layout
        self.samples_frame.layout().addRow(self.sample_name, self.is_reference)
        self.samples_frame.layout().addRow(self.add_sample_button, self.remove_sample_button)

        # ## Sample table
        self.sample_table = QTableWidget(self.samples_page)
        self.sample_table.setGeometry(self.margin['left'],
                                      self.widget_vposition(self.samples_frame) + 5, self.stretch(), 350)
        self.sample_table.setColumnCount(2)
        self.sample_table.setHorizontalHeaderItem(0, QTableWidgetItem('Sample'))
        self.sample_table.setHorizontalHeaderItem(1, QTableWidgetItem('Reference?'))
        head = self.sample_table.horizontalHeader()
        head.setSectionResizeMode(0, QHeaderView.Stretch)
        head.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        # ## Save & clear buttons
        # Save & clear frame (invisible)
        self.saveclear_frame = QFrame(self.samples_page)
        self.saveclear_frame.setGeometry(self.margin['left'],
                                         self.widget_vposition(self.sample_table) + 5, self.stretch(), 30)
        saveclear_layout = QHBoxLayout()
        saveclear_layout.setMargin(0)
        self.saveclear_frame.setLayout(saveclear_layout)
        # Clear samples button
        self.clear_samples = QPushButton(self.samples_page)
        self.set_icon(self.clear_samples, 'clear')
        self.clear_samples.setText(' Clear table')
        self.clear_samples.setStyleSheet(self.style['button'])
        self.clear_samples.clicked.connect(self.prompt_clear_data)
        # Save samples button
        self.save_samples = QPushButton(self.samples_page)
        self.set_icon(self.save_samples, 'ok')
        self.save_samples.setText(' Save samples')
        self.save_samples.setStyleSheet(self.style['button'])
        self.save_samples.clicked.connect(self.goto_main_page)
        # Add widgets above to save & clear layout
        self.saveclear_frame.layout().addWidget(self.clear_samples)
        self.saveclear_frame.layout().addWidget(self.save_samples)

        # ###
        # ### GATING PAGE
        # ###

        # ## Title section
        # Title
        self.gates_title = QLabel(self.gates_page)
        self.gates_title.move(self.margin['left'], self.margin['top'])
        self.gates_title.setText('Gating & outlier options')
        self.gates_title.setStyleSheet(self.style['title'])
        self.gates_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.gates_title.adjustSize()

        # ## Gating options section
        # Gating header
        self.gate_header = QLabel(self.gates_page)
        self.gate_header.move(self.margin['left'], self.widget_vposition(self.gates_title) + 25)
        self.gate_header.setText('Gating')
        self.gate_header.setStyleSheet(self.style['header'])
        self.gate_header.adjustSize()
        # Gating frame
        self.gate_frame = QFrame(self.gates_page)
        self.gate_frame.setGeometry(self.margin['left'],
                                    self.widget_vposition(self.gate_header) + 5, self.stretch(), 150)
        self.gate_frame.setFrameShape(QFrame.StyledPanel)
        self.gate_frame.setLayout(QFormLayout())
        # Gating button group
        self.gating_group = QButtonGroup(self)
        # Do not gate samples
        self.no_gates = QRadioButton(self.gates_page)
        self.no_gates.setObjectName('no')
        self.no_gates.setText("Don't gate samples")
        self.no_gates.setChecked(True)
        self.gating_group.addButton(self.no_gates)
        self.no_gates.clicked.connect(self.activate_gate)
        # CyToF gating
        self.cytof_gates = QRadioButton(self.gates_page)
        self.cytof_gates.setObjectName('cytof')
        cytof_info = ('Mass Cytometry gating - exclude samples with\n'
                      'average expression for all markers below:')
        self.cytof_gates.setText(cytof_info)
        self.gating_group.addButton(self.cytof_gates)
        self.cytof_gates.clicked.connect(self.activate_gate)
        # CyToF gating spinbox
        self.cytof_gates_value = QDoubleSpinBox(self.gates_page)
        self.cytof_gates_value.setMinimum(0)
        self.cytof_gates_value.setMaximum(1)
        self.cytof_gates_value.setValue(0.1)
        self.cytof_gates_value.setSingleStep(0.05)
        self.cytof_gates_value.setEnabled(False)
        # scRNA-Seq gating
        self.rnaseq_gates = QRadioButton(self.gates_page)
        rnaseq_info = ('scRNA-Seq gating - when calculating cutoff,'
                       '\nexclude number of reads below:')
        self.rnaseq_gates.setText(rnaseq_info)
        self.rnaseq_gates.setObjectName('rnaseq')
        self.gating_group.addButton(self.rnaseq_gates)
        self.rnaseq_gates.clicked.connect(self.activate_gate)
        # scRNA-Seq gating spinbox
        self.rnaseq_gates_value = QDoubleSpinBox(self.gates_page)
        self.rnaseq_gates_value.setMinimum(0)
        self.rnaseq_gates_value.setMaximum(10)
        self.rnaseq_gates_value.setValue(1)
        self.rnaseq_gates_value.setSingleStep(1)
        self.rnaseq_gates_value.setEnabled(False)
        # Add widgets above to Gate frame layout
        self.gate_frame.layout().addRow(self.no_gates, QLabel())
        self.gate_frame.layout().addRow(self.cytof_gates, self.cytof_gates_value)
        self.gate_frame.layout().addRow(self.rnaseq_gates, self.rnaseq_gates_value)

        # ## Outlier options section
        # Outlier header
        self.outlier_header = QLabel(self.gates_page)
        self.outlier_header.move(self.margin['left'], self.widget_vposition(self.gate_frame) + 25)
        self.outlier_header.setText('Outliers')
        self.outlier_header.setStyleSheet(self.style['header'])
        self.outlier_header.adjustSize()
        # Outlier frame
        self.outlier_frame = QFrame(self.gates_page)
        self.outlier_frame.setGeometry(self.margin['left'],
                                       self.widget_vposition(self.outlier_header) + 5, self.stretch(), 100)
        self.outlier_frame.setFrameShape(QFrame.StyledPanel)
        self.outlier_frame.setLayout(QVBoxLayout())
        # Bottom outliers data
        self.bottom_outliers = QCheckBox(self.gates_page)
        self.bottom_outliers.setText('Also generate results for low outliers')
        # Non-outliers data
        self.not_outliers = QCheckBox(self.gates_page)
        self.not_outliers.setText('Also generate results for non-outliers')
        # Add widgets above to Gate frame layout
        self.outlier_frame.layout().addWidget(self.bottom_outliers)
        self.outlier_frame.layout().addWidget(self.not_outliers)

        # ## Save/back button
        self.save_gates = QPushButton(self.gates_page)
        self.save_gates.setGeometry(self.margin['left'],
                                    self.widget_vposition(self.outlier_frame) + 25, self.stretch(), 40)
        self.set_icon(self.save_gates, 'ok')
        self.save_gates.setText(' Back to main page')
        self.save_gates.clicked.connect(self.goto_main_page)

    # ###
    # ### STATIC METHODS
    # ###

    @staticmethod
    def widget_hposition(widget: QWidget) -> int:
        return widget.width() + widget.x()

    @staticmethod
    def widget_vposition(widget: QWidget) -> int:
        return widget.height() + widget.y()

    @staticmethod
    def set_icon(widget: QWidget, icon: str) -> None:
        i = QIcon()
        i.addPixmap(QPixmap(os.path.join('icons', f'{icon}.svg')))
        widget.setIcon(i)

    @staticmethod
    def get_help() -> None:
        webbrowser.open('https://scouts.readthedocs.io/en/master/')

    def stretch(self) -> int:
        return self.size['width'] - (self.margin['left'] + self.margin['right'])

    def closeEvent(self, event: QEvent) -> None:
        title = 'Quit Application'
        mes = "Are you sure you want to quit?"
        reply = QMessageBox.question(self, title, mes,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # ###
    # ### STACKED WIDGET PAGE SWITCHING
    # ###

    def goto_main_page(self) -> None:
        self.stacked_pages.setCurrentWidget(self.main_page)

    def goto_samples_page(self) -> None:
        self.stacked_pages.setCurrentWidget(self.samples_page)

    def goto_gates_page(self) -> None:
        self.stacked_pages.setCurrentWidget(self.gates_page)

    # ###
    # ### I/O PATH LOGIC
    # ###

    def get_path(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        name = self.sender().objectName()
        if name == 'input':
            echo = self.input_path
            query, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All Files (*)", options=options)
        elif name == 'output':
            echo = self.output_path
            query = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        else:
            return
        if query:
            echo.setText(query)

    # ###
    # ### SAMPLE NAME/SAMPLE TABLE GUI LOGIC
    # ###

    def write_to_sample_table(self) -> None:
        table = self.sample_table
        ref = 'No'
        sample = self.sample_name.text()
        if sample:
            for cell in range(table.rowCount()):
                item = table.item(cell, 0)
                if item.text() == sample:
                    self.same_sample()
                    return
            if self.is_reference.isChecked():
                for cell in range(table.rowCount()):
                    item = table.item(cell, 1)
                    if item.text() == 'Yes':
                        self.more_than_one_reference()
                        return
                ref = 'Yes'
            sample = QTableWidgetItem(sample)
            is_reference = QTableWidgetItem(ref)
            is_reference.setFlags(Qt.ItemIsEnabled)
            row_position = table.rowCount()
            table.insertRow(row_position)
            table.setItem(row_position, 0, sample)
            table.setItem(row_position, 1, is_reference)
            self.is_reference.setChecked(False)
            self.sample_name.setText('')

    def remove_from_sample_table(self) -> None:
        table = self.sample_table
        rows = set(index.row() for index in table.selectedIndexes())
        for index in sorted(rows, reverse=True):
            self.sample_table.removeRow(index)

    def prompt_clear_data(self) -> None:
        if self.confirm_clear_data():
            table = self.sample_table
            while table.rowCount():
                self.sample_table.removeRow(0)

    # ###
    # ### GATING GUI LOGIC
    # ###

    def activate_gate(self) -> None:
        if self.sender().objectName() == 'no':
            self.cytof_gates_value.setEnabled(False)
            self.rnaseq_gates_value.setEnabled(False)
        elif self.sender().objectName() == 'cytof':
            self.cytof_gates_value.setEnabled(True)
            self.rnaseq_gates_value.setEnabled(False)
        elif self.sender().objectName() == 'rnaseq':
            self.cytof_gates_value.setEnabled(False)
            self.rnaseq_gates_value.setEnabled(True)

    # ###
    # ### CONNECT SCOUTS TO ANALYTICAL MODULES
    # ###

    def analyse(self) -> None:
        try:
            input_dict = self.parse_input()
            analyse(self, **input_dict)
        except Exception as e:
            if type(e) not in CUSTOM_ERRORS:
                raise GenericError(self)
        else:
            self.module_done()

    def parse_input(self) -> Dict:
        input_dict = {}
        # Input and output
        input_file = self.input_path.text()
        output_folder = self.output_path.text()
        if not (input_file or output_folder):
            raise NoIOPathError(self)
        input_dict['input_file'] = input_file
        input_dict['output_folder'] = output_folder
        # Set cutoff by reference or by sample rule
        cutoff_id = self.cutoff_group.checkedId()
        cutoff_rule = self.cutoff_group.button(cutoff_id)
        input_dict['cutoff_rule'] = cutoff_rule.text()  # 'sample', 'reference', 'both'
        # Outliers for each individual marker or any marker in row
        markers_id = self.markers_group.checkedId()
        markers_rule = self.markers_group.button(markers_id)
        input_dict['marker_rule'] = markers_rule.text()  # 'single marker', 'any marker', 'both methods'
        # Tukey factor used for calculating cutoff
        tukey_id = self.tukey_group.checkedId()
        tukey = self.tukey_group.button(tukey_id)
        input_dict['tukey_factor'] = float(tukey.text())  # '1.5', '3.0'
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
        if self.single_excel.isChecked():
            single_excel = True
        else:
            single_excel = False
        input_dict['single_excel'] = single_excel
        # Retrieve samples from sample table
        sample_list = []
        for tuples in self.yield_samples_from_table():
            sample_list.append(tuples)
        if not sample_list:
            raise NoSampleError(self)
        input_dict['sample_list'] = sample_list
        # Set gate cutoff (if any)
        input_dict['gate_cutoff'] = None
        if not self.no_gates.isChecked():
            if self.cytof_gates.isChecked():
                input_dict['gate_cutoff'] = self.gates_cytof_value.value()
            if self.rnaseq_gates.isChecked():
                input_dict['gate_cutoff'] = self.rnaseq_gates_value.value()
        # Generate results for non-outliers
        non_outliers = False
        if self.not_outliers.isChecked():
            non_outliers = True
        input_dict['non_outliers'] = non_outliers
        # Generate results for bottom outliers
        bottom_outliers = False
        if self.bottom_outliers.isChecked():
            bottom_outliers = True
        input_dict['bottom_outliers'] = bottom_outliers
        # return dictionary with all gathered inputs
        return input_dict

    def yield_samples_from_table(self) -> Generator[Tuple[str, str], None, None]:
        table = self.sample_table
        for cell in range(table.rowCount()):
            sample_name = table.item(cell, 0).text()
            sample_type = table.item(cell, 1).text()
            yield sample_name, sample_type

    # ###
    # ### MESSAGE BOXES
    # ###

    def module_done(self) -> None:
        title = "Analysis finished!"
        mes = "Your analysis has finished. No errors were reported."
        QMessageBox.information(self, title, mes)

    def memory_warning(self) -> None:
        if self.sender().isChecked():
            title = 'Warning!'
            mes = ("Depending on your dataset, this option can consume a LOT of memory. "
                   "Please make sure that your computer can handle it!")
            QMessageBox.critical(self, title, mes)

    def same_sample(self) -> None:
        title = 'Error: sample name already in table'
        mes = ("Sorry, you can't do this because this sample name is already in the table. "
               "Please select a different name.")
        QMessageBox.critical(self, title, mes)

    def more_than_one_reference(self) -> None:
        title = "Error: more than one reference selected"
        mes = ("Sorry, you can't do this because there is already a reference column in the table. "
               "Please remove it before adding a reference.")
        QMessageBox.critical(self, title, mes)

    def confirm_clear_data(self) -> bool:
        title = 'Confirm Action'
        mes = "Table will be cleared. Are you sure?"
        reply = QMessageBox.question(self, title, mes, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scouts = SCOUTS()
    scouts.show()
    sys.exit(app.exec_())
