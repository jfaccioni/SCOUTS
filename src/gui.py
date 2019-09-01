from __future__ import annotations

import os
import sys
import traceback
import webbrowser
from typing import Dict, Generator, TYPE_CHECKING, Tuple

# noinspection PyUnresolvedReferences
from PySide2.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal, Slot
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QDoubleSpinBox, QFileDialog,
                               QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
                               QMessageBox, QPushButton, QRadioButton, QStackedWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from src.analysis import start_scouts
from src.interface import Worker
from src.utils import (EmptySampleListError, NoIOPathError, NoReferenceError, NoSampleError, PandasInputError,
                       SampleNamingError, get_project_root)

if TYPE_CHECKING:
    from PySide2.QtCore import QEvent


class SCOUTS(QMainWindow):
    """Main Window Widget for SCOUTS."""
    margin = {
        'left': 15,
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
        """SCOUTS Constructor. Defines all aspects of the GUI."""

        # ###
        # ### Main Window setup
        # ###

        # Inherits from QMainWindow
        super().__init__()
        self.root = get_project_root()

        self.threadpool = QThreadPool()
        # Sets values for QMainWindow
        self.setWindowTitle("SCOUTS")
        self.setWindowIcon(QIcon(os.path.abspath(os.path.join(self.root, 'src', 'icons', f'scouts.ico'))))
        self.resize(*self.size.values())
        # Creates StackedWidget as QMainWindow's central widget
        self.stacked_pages = QStackedWidget(self)
        self.setCentralWidget(self.stacked_pages)
        # Creates Widgets for individual "pages" and adds them to the StackedWidget
        self.main_page = QWidget()
        self.samples_page = QWidget()
        self.gating_page = QWidget()
        self.pages = (self.main_page, self.samples_page, self.gating_page)
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
                                     self.widget_vposition(self.input_header) + 5, self.rlimit(), 105)
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
        self.samples_button.setText(' Name samples...')
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
                                        self.widget_vposition(self.analysis_header) + 5, self.rlimit(), 155)
        self.analysis_frame.setFrameShape(QFrame.StyledPanel)
        self.analysis_frame.setLayout(QVBoxLayout())
        # Cutoff text
        self.cutoff_text = QLabel(self.main_page)
        self.cutoff_text.setText('For each sample, consider outliers using cutoff value from:')
        self.cutoff_text.setStyleSheet(self.style['bold-label'])
        # Cutoff button group
        self.cutoff_group = QButtonGroup(self)
        # Cutoff by sample
        self.cutoff_sample = QRadioButton(self.main_page)
        self.cutoff_sample.setText('the sample itself')
        self.cutoff_sample.setObjectName('sample')
        self.cutoff_sample.setStyleSheet(self.style['radio button'])
        self.cutoff_sample.setChecked(True)
        self.cutoff_group.addButton(self.cutoff_sample)
        # Cutoff by reference
        self.cutoff_reference = QRadioButton(self.main_page)
        self.cutoff_reference.setText('a reference sample')
        self.cutoff_reference.setObjectName('ref')
        self.cutoff_reference.setStyleSheet(self.style['radio button'])
        self.cutoff_group.addButton(self.cutoff_reference)
        # Both cutoffs
        self.cutoff_both = QRadioButton(self.main_page)
        self.cutoff_both.setText('both')
        self.cutoff_both.setObjectName('sample ref')
        self.cutoff_both.setStyleSheet(self.style['radio button'])
        self.cutoff_group.addButton(self.cutoff_both)
        # Markers text
        self.markers_text = QLabel(self.main_page)
        self.markers_text.setStyleSheet(self.style['bold-label'])
        self.markers_text.setText('Select outliers for:')
        # Markers button group
        self.markers_group = QButtonGroup(self)
        # Single marker
        self.single_marker = QRadioButton(self.main_page)
        self.single_marker.setText('each individual marker')
        self.single_marker.setObjectName('single')
        self.single_marker.setStyleSheet(self.style['radio button'])
        self.single_marker.setChecked(True)
        self.markers_group.addButton(self.single_marker)
        # Any marker
        self.any_marker = QRadioButton(self.main_page)
        self.any_marker.setText('any marker')
        self.any_marker.setObjectName('any')
        self.any_marker.setStyleSheet(self.style['radio button'])
        self.markers_group.addButton(self.any_marker)
        # Both methods
        self.both_methods = QRadioButton(self.main_page)
        self.both_methods.setText('both')
        self.both_methods.setObjectName('single any')
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
                                      self.widget_vposition(self.output_header) + 5, self.rlimit(), 140)
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
        self.output_csv.setChecked(True)
        # Generate XLSX checkbox
        self.output_excel = QCheckBox(self.main_page)
        self.output_excel.setText('Export multiple Excel spreadsheets (.xlsx)')
        self.output_excel.setStyleSheet(self.style['checkbox'])
        self.output_excel.clicked.connect(self.enable_single_excel)
        # Generate single, large XLSX checkbox
        self.single_excel = QCheckBox(self.main_page)
        self.single_excel.setText('Also save one Excel spreadsheet\nwith each analysis in individual sheets')
        self.single_excel.setStyleSheet(self.style['checkbox'])
        self.single_excel.setEnabled(False)
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
                                    self.widget_vposition(self.output_frame) + 5, self.rlimit(), 30)
        self.set_icon(self.run_button, 'pipe')
        self.run_button.setText(' Run!')
        self.run_button.setText(' Run!')
        self.run_button.clicked.connect(self.run)
        # Help-quit frame (invisible)
        self.helpquit_frame = QFrame(self.main_page)
        self.helpquit_frame.setGeometry(self.margin['left'],
                                        self.widget_vposition(self.run_button) + 5, self.rlimit(), 30)
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
                                       self.widget_vposition(self.samples_subtitle) + 5, self.rlimit(), 80)
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
                                      self.widget_vposition(self.samples_frame) + 5, self.rlimit(), 350)
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
                                         self.widget_vposition(self.sample_table) + 5, self.rlimit(), 30)
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
        self.gates_title = QLabel(self.gating_page)
        self.gates_title.move(self.margin['left'], self.margin['top'])
        self.gates_title.setText('Gating & outlier options')
        self.gates_title.setStyleSheet(self.style['title'])
        self.gates_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.gates_title.adjustSize()

        # ## Gating options section
        # Gating header
        self.gate_header = QLabel(self.gating_page)
        self.gate_header.move(self.margin['left'], self.widget_vposition(self.gates_title) + 25)
        self.gate_header.setText('Gating')
        self.gate_header.setStyleSheet(self.style['header'])
        self.gate_header.adjustSize()
        # Gating frame
        self.gate_frame = QFrame(self.gating_page)
        self.gate_frame.setGeometry(self.margin['left'],
                                    self.widget_vposition(self.gate_header) + 5, self.rlimit(), 150)
        self.gate_frame.setFrameShape(QFrame.StyledPanel)
        self.gate_frame.setLayout(QFormLayout())
        # Gating button group
        self.gating_group = QButtonGroup(self)
        # Do not gate samples
        self.no_gates = QRadioButton(self.gating_page)
        self.no_gates.setObjectName('no_gate')
        self.no_gates.setText("Don't gate samples")
        self.no_gates.setChecked(True)
        self.gating_group.addButton(self.no_gates)
        self.no_gates.clicked.connect(self.activate_gate)
        # CyToF gating
        self.cytof_gates = QRadioButton(self.gating_page)
        self.cytof_gates.setObjectName('cytof')
        cytof_info = 'Mass Cytometry gating - exclude samples with\naverage expression for all markers below:'
        self.cytof_gates.setText(cytof_info)
        self.gating_group.addButton(self.cytof_gates)
        self.cytof_gates.clicked.connect(self.activate_gate)
        # CyToF gating spinbox
        self.cytof_gates_value = QDoubleSpinBox(self.gating_page)
        self.cytof_gates_value.setMinimum(0)
        self.cytof_gates_value.setMaximum(1)
        self.cytof_gates_value.setValue(0.1)
        self.cytof_gates_value.setSingleStep(0.05)
        self.cytof_gates_value.setEnabled(False)
        # scRNA-Seq gating
        self.rnaseq_gates = QRadioButton(self.gating_page)
        rnaseq_info = 'scRNA-Seq gating - when calculating cutoff,\nexclude number of reads below:'
        self.rnaseq_gates.setText(rnaseq_info)
        self.rnaseq_gates.setObjectName('rnaseq')
        self.gating_group.addButton(self.rnaseq_gates)
        self.rnaseq_gates.clicked.connect(self.activate_gate)
        # scRNA-Seq gating spinbox
        self.rnaseq_gates_value = QDoubleSpinBox(self.gating_page)
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
        self.outlier_header = QLabel(self.gating_page)
        self.outlier_header.move(self.margin['left'], self.widget_vposition(self.gate_frame) + 25)
        self.outlier_header.setText('Outliers')
        self.outlier_header.setStyleSheet(self.style['header'])
        self.outlier_header.adjustSize()
        # Outlier frame
        self.outlier_frame = QFrame(self.gating_page)
        self.outlier_frame.setGeometry(self.margin['left'],
                                       self.widget_vposition(self.outlier_header) + 5, self.rlimit(), 100)
        self.outlier_frame.setFrameShape(QFrame.StyledPanel)
        self.outlier_frame.setLayout(QVBoxLayout())
        # Top outliers information
        self.top_outliers = QLabel(self.gating_page)
        self.top_outliers.setStyleSheet(self.style['label'])
        self.top_outliers.setText('By default, SCOUTS selects the top outliers from the population')
        # Bottom outliers data
        self.bottom_outliers = QCheckBox(self.gating_page)
        self.bottom_outliers.setText('Also generate results for low outliers')
        # Non-outliers data
        self.not_outliers = QCheckBox(self.gating_page)
        self.not_outliers.setText('Also generate results for non-outliers')
        # Add widgets above to Gate frame layout
        self.outlier_frame.layout().addWidget(self.top_outliers)
        self.outlier_frame.layout().addWidget(self.bottom_outliers)
        self.outlier_frame.layout().addWidget(self.not_outliers)

        # ## Save/back button
        self.save_gates = QPushButton(self.gating_page)
        self.save_gates.setGeometry(self.margin['left'],
                                    self.widget_vposition(self.outlier_frame) + 25, self.rlimit(), 40)
        self.set_icon(self.save_gates, 'ok')
        self.save_gates.setText(' Back to menu')
        self.save_gates.clicked.connect(self.goto_main_page)

    # ###
    # ### WIDGET ADJUSTMENT METHODS
    # ###

    def rlimit(self) -> int:
        """Returns the X position of the start of the right margin. Used to stretch Widgets across the GUI."""
        return self.size['width'] - (self.margin['left'] + self.margin['right'])

    @staticmethod
    def widget_hposition(widget: QWidget) -> int:
        """Returns the X position of the rightmost part of the widget."""
        return widget.width() + widget.x()

    @staticmethod
    def widget_vposition(widget: QWidget) -> int:
        """Returns the Y position of the bottommost part of the widget."""
        return widget.height() + widget.y()

    def set_icon(self, widget: QWidget, icon: str) -> None:
        """Associates an icon to a widget."""
        i = QIcon()
        i.addPixmap(QPixmap(os.path.abspath(os.path.join(self.root, 'src', 'icons', f'{icon}.svg'))))
        widget.setIcon(i)

    # ###
    # ### STACKED WIDGET PAGE SWITCHING
    # ###

    def goto_main_page(self) -> None:
        """Switches stacked widget pages to the main page."""
        self.stacked_pages.setCurrentWidget(self.main_page)

    def goto_samples_page(self) -> None:
        """Switches stacked widget pages to the samples table page."""
        self.stacked_pages.setCurrentWidget(self.samples_page)

    def goto_gates_page(self) -> None:
        """Switches stacked widget pages to the gating & other options page."""
        self.stacked_pages.setCurrentWidget(self.gating_page)

    # ###
    # ### MAIN PAGE GUI LOGIC
    # ###

    def get_path(self) -> None:
        """Opens a dialog box and sets the chosen file/folder path, depending on the caller widget."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        if self.sender().objectName() == 'input':
            query, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All Files (*)", options=options)
        elif self.sender().objectName() == 'output':
            query = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        else:
            return
        if query:
            self.sender().setText(query)

    def enable_single_excel(self):
        """Enables checkbox for generating a single Excel output."""
        if self.output_excel.isChecked():
            self.single_excel.setEnabled(True)
        else:
            self.single_excel.setEnabled(False)
            self.single_excel.setChecked(False)

    # ###
    # ### SAMPLE NAME/SAMPLE TABLE GUI LOGIC
    # ###

    def write_to_sample_table(self) -> None:
        """Writes data to sample table."""
        table = self.sample_table
        ref = 'no'
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
                    if item.text() == 'yes':
                        self.more_than_one_reference()
                        return
                ref = 'yes'
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
        """Removes data from sample table."""
        table = self.sample_table
        rows = set(index.row() for index in table.selectedIndexes())
        for index in sorted(rows, reverse=True):
            self.sample_table.removeRow(index)

    def prompt_clear_data(self) -> None:
        """Prompts option to clear all data in the sample table."""
        if self.confirm_clear_data():
            table = self.sample_table
            while table.rowCount():
                self.sample_table.removeRow(0)

    # ###
    # ### GATING GUI LOGIC
    # ###

    def activate_gate(self) -> None:
        """Activates/deactivates buttons related to gating."""
        if self.sender().objectName() == 'no_gate':
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

    def run(self) -> None:
        """Runs SCOUTS based on user input in the GUI."""
        try:
            data = self.parse_input()
        except Exception as error:
            self.propagate_error(error)
        else:
            worker = Worker(func=start_scouts, widget=self, **data)
            worker.signals.started.connect(self.analysis_has_started)
            worker.signals.finished.connect(self.analysis_has_finished)
            worker.signals.success.connect(self.success_message)
            worker.signals.error.connect(self.propagate_error)
            self.threadpool.start(worker)

    def parse_input(self) -> Dict:
        """Returns user input on the GUI as a dictionary."""
        # Input and output
        input_dict = {'input_file': str(self.input_path.text()), 'output_folder': str(self.output_path.text())}
        if not input_dict['input_file'] or not input_dict['output_folder']:
            raise NoIOPathError
        # Set cutoff by reference or by sample rule
        input_dict['cutoff_rule'] = self.cutoff_group.checkedButton().objectName()  # 'sample', 'ref', 'sample ref'
        # Outliers for each individual marker or any marker in row
        input_dict['marker_rule'] = self.markers_group.checkedButton().objectName()  # 'single', 'any', 'single any'
        # Tukey factor used for calculating cutoff
        input_dict['tukey_factor'] = float(self.tukey_group.checkedButton().text())  # '1.5', '3.0'
        # Output settings
        input_dict['export_csv'] = False
        if self.output_csv.isChecked():
            input_dict['export_csv'] = True
        input_dict['export_excel'] = False
        if self.output_excel.isChecked():
            input_dict['export_excel'] = True
        input_dict['single_excel'] = False
        if self.single_excel.isChecked():
            input_dict['single_excel'] = True
        # Retrieve samples from sample table
        input_dict['sample_list'] = []
        for tuples in self.yield_samples_from_table():
            input_dict['sample_list'].append(tuples)
        if not input_dict['sample_list']:
            raise NoSampleError
        # Set gate cutoff (if any)
        input_dict['gate_cutoff_value'] = None
        input_dict['gating'] = self.gating_group.checkedButton().objectName()  # 'no_gate', 'cytof', 'rnaseq'
        if not self.no_gates.isChecked():
            input_dict['gating_value'] = getattr(self, f'{input_dict["gating"]}_gates_value').value()
        # Generate results for non-outliers
        input_dict['non_outliers'] = False
        if self.not_outliers.isChecked():
            input_dict['non_outliers'] = True
        # Generate results for bottom outliers
        input_dict['bottom_outliers'] = False
        if self.bottom_outliers.isChecked():
            input_dict['bottom_outliers'] = True
        # return dictionary with all gathered inputs
        return input_dict

    def yield_samples_from_table(self) -> Generator[Tuple[str, str], None, None]:
        """Yields sample names from the sample table."""
        table = self.sample_table
        for cell in range(table.rowCount()):
            sample_name = table.item(cell, 0).text()
            sample_type = table.item(cell, 1).text()
            yield sample_name, sample_type

    # ###
    # ### MESSAGE BOXES
    # ###

    def analysis_has_started(self):
        self.run_button.setEnabled(False)

    def analysis_has_finished(self):
        self.run_button.setEnabled(True)

    def success_message(self) -> None:
        """Info message box used when SCOUTS finished without errors."""
        title = "Analysis finished!"
        mes = "Your analysis has finished. No errors were reported."
        if self.isEnabled() is True:
            QMessageBox.information(self, title, mes)

    def memory_warning(self) -> None:
        """Warning message box used when user wants to generate a single excel file."""
        if self.sender().isChecked():
            title = 'Memory warning!'
            mes = ("Depending on your dataset, this option can consume a LOT of memory and take"
                   " a long time to process. Please make sure that your computer can handle it!")
            QMessageBox.information(self, title, mes)

    def same_sample(self) -> None:
        """Error message box used when the user tries to input the same sample twice in the sample table."""
        title = 'Error: sample name already in table'
        mes = ("Sorry, you can't do this because this sample name is already in the table. "
               "Please select a different name.")
        QMessageBox.critical(self, title, mes)

    def more_than_one_reference(self) -> None:
        """Error message box used when the user tries to input two reference samples in the sample table."""
        title = "Error: more than one reference selected"
        mes = ("Sorry, you can't do this because there is already a reference column in the table. "
               "Please remove it before adding a reference.")
        QMessageBox.critical(self, title, mes)

    def confirm_clear_data(self) -> bool:
        """Question message box used to confirm user action of clearing sample table."""
        title = 'Confirm Action'
        mes = "Table will be cleared. Are you sure?"
        reply = QMessageBox.question(self, title, mes, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False

    # ###
    # ### EXCEPTIONS & ERRORS
    # ###

    def propagate_error(self, error):
        if isinstance(error, EmptySampleListError):
            self.empty_sample_list_error_message()
        if isinstance(error, NoIOPathError):
            self.no_io_path_error_message()
        elif isinstance(error, NoReferenceError):
            self.no_reference_error_message()
        elif isinstance(error, NoSampleError):
            self.no_sample_error_message()
        elif isinstance(error, PandasInputError):
            self.pandas_input_error_message()
        elif isinstance(error, SampleNamingError):
            self.sample_naming_error_message()
        else:
            trace = traceback.format_exc()
            self.generic_error_message(error, trace)

    def empty_sample_list_error_message(self) -> None:
        title = 'Error: No control sample'
        message = ("Sorry, your samples do not include a control. Please make sure to "
                   "tag one of the samples as a control.")
        QMessageBox.critical(self, title, message)

    def no_io_path_error_message(self) -> None:
        title = 'Error: no file/folder'
        message = ("Sorry, no input file and/or output folder was provided. "
                   "Please add the path to the necessary file/folder.")
        QMessageBox.critical(self, title, message)

    def no_reference_error_message(self) -> None:
        title = "Error: No reference selected"
        message = ("Sorry, no reference sample was found on the sample list, but analysis was set to "
                   "reference. Please add a reference sample, or change the rule for cutoff calculation.")
        QMessageBox.critical(self, title, message)

    def no_sample_error_message(self) -> None:
        title = "Error: No samples selected"
        message = ("Sorry, the analysis cannot be performed because no sample names were input. "
                   "Please add your sample names.")
        QMessageBox.critical(self, title, message)

    def pandas_input_error_message(self) -> None:
        title = 'Error: unexpected input file'
        message = ("Sorry, the input file could not be read. Please make sure that "
                   "the data is save in a valid format (supported formats are: "
                   ".csv, .xlsx).")
        QMessageBox.critical(self, title, message)

    def sample_naming_error_message(self) -> None:
        title = 'Error: sample names not in input file'
        message = ("Sorry, your sample names were not found in the input file. Please "
                   "make sure that the names were typed correctly (case-sensitive).")
        QMessageBox.critical(self, title, message)

    def generic_error_message(self, error, trace) -> None:
        """Error message box used to display any error message (including traceback) for any uncaught errors."""
        title = 'An error occurred!'
        QMessageBox.critical(self, title, f"{str(error)}\n\nfull traceback:\n{str(trace)}")

    def not_implemented_error_message(self) -> None:
        """Error message box used when the user accesses a functionality that hasn't been implemented yet."""
        title = "Not yet implemented"
        mes = "Sorry, this functionality has not been implemented yet."
        QMessageBox.critical(self, title, mes)

    # ###
    # ### HELP & QUIT
    # ###

    @staticmethod
    def get_help() -> None:
        """Opens SCOUTS documentation on the browser. Called when the user clicks the "help" button"""
        webbrowser.open('https://scouts.readthedocs.io/en/master/')

    def closeEvent(self, event: QEvent) -> None:
        """Defines the message box for when the user wants to quit SCOUTS."""
        title = 'Quit SCOUTS'
        mes = "Are you sure you want to quit?"
        reply = QMessageBox.question(self, title, mes, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.setEnabled(False)
            self.threadpool.waitForDone()  # TODO: figure out how to present a message box while waiting for threads
            event.accept()
        else:
            event.ignore()

    # ###
    # ### DEBUG OPTIONS
    # ###

    def debug(self):
        """Pre-loads GUI elements if debug flag is set."""
        gio_data = True
        laptop = True
        repo = 'SCOUTS'
        if laptop:
            repo = 'scouts'
        if gio_data:
            inp = (f'/home/juliano/Repositories/my-github-repositories/{repo}/local/'
                   'giovana files/other sample/raw_data.xlsx')
            self.input_path.setText(inp)
            out = (f'/home/juliano/Repositories/my-github-repositories/{repo}/local/'
                   'giovana files/other sample/scouts output')
            self.output_path.setText(out)
            self.sample_table.insertRow(0)
            self.sample_table.setItem(0, 0, QTableWidgetItem('Pre-Tx'))
            self.sample_table.setItem(0, 1, QTableWidgetItem('yes'))
            self.sample_table.insertRow(1)
            self.sample_table.setItem(1, 0, QTableWidgetItem('Week4'))
            self.sample_table.setItem(1, 1, QTableWidgetItem('no'))
        else:
            inp = '/home/juliano/Repositories/my-github-repositories/SCOUTS/examples/mass-cytometry template.xlsx'
            self.input_path.setText(inp)
            out = '/home/juliano/Repositories/my-github-repositories/SCOUTS/local/output'
            self.output_path.setText(out)
            self.sample_table.insertRow(0)
            self.sample_table.setItem(0, 0, QTableWidgetItem('Ct'))
            self.sample_table.setItem(0, 1, QTableWidgetItem('yes'))
            self.sample_table.insertRow(1)
            self.sample_table.setItem(1, 0, QTableWidgetItem('RT'))
            self.sample_table.setItem(1, 1, QTableWidgetItem('no'))
            self.sample_table.insertRow(2)
            self.sample_table.setItem(2, 0, QTableWidgetItem('Torin'))
            self.sample_table.setItem(2, 1, QTableWidgetItem('no'))


# Automatically fills fields for quick testing
DEBUG = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scouts = SCOUTS()
    if DEBUG:
        scouts.debug()
    scouts.show()
    sys.exit(app.exec_())
