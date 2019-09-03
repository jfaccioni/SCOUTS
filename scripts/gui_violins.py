from __future__ import annotations

import os
import sys
import traceback
from typing import Generator, List, TYPE_CHECKING

# noinspection PyUnresolvedReferences,PyPackageRequirements
import matplotlib
# noinspection PyUnresolvedReferences,PyPackageRequirements
from matplotlib.figure import Figure
# noinspection PyUnresolvedReferences,PyPackageRequirements
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
# noinspection PyUnresolvedReferences,PyPackageRequirements
import seaborn as sns
from PySide2.QtCore import QThreadPool, Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import (QApplication, QComboBox, QFileDialog, QFormLayout, QFrame, QLabel, QLineEdit,
                               QMainWindow, QMessageBox, QPushButton, QWidget, QSizePolicy)

from src.interface import Worker
from src.utils import get_project_root

if TYPE_CHECKING:
    from PySide2.QtCore import QEvent

matplotlib.use('Qt5Agg')
sns.set(style="whitegrid")


class ViolinGUI(QMainWindow):
    """Main Window Widget for ViolinGUI."""
    margin = {
        'left': 15,
        'top': 5,
        'right': 10,
        'bottom': 10
    }
    size = {
        'width': 360,
        'height': 480
    }
    style = {
        'title': 'QLabel {font-size:18pt; font-weight:700}',
        'header': 'QLabel {font-weight:600}',
        'button': 'QPushButton {font-size: 10pt}',
        'label': 'QLabel {font-size: 10pt}',
        'line edit': 'QLineEdit {font-size: 10pt}',
    }

    def __init__(self) -> None:
        """ViolinGUI Constructor. Defines all aspects of the GUI."""
        # ## Setup section
        # Inherits from QMainWindow
        super().__init__()
        # QMainWindow basic properties
        self.setWindowTitle("Plot Violins")
        self.root = get_project_root()
        self.setMinimumSize(*self.size.values())
        self.setMaximumSize(*self.size.values())
        # Creates QWidget as QMainWindow's central widget
        self.page = QWidget(self)
        self.setCentralWidget(self.page)
        # Miscellaneous initialization values
        self.threadpool = QThreadPool()  # Threadpool for workers
        self.population_df = None  # DataFrame of whole population (raw data)
        self.summary_df = None  # DataFrame indicating which SCOUTS output corresponds to which rule
        self.summary_path = None  # path to all DataFrames generated by SCOUTS

        # Title section
        # Title
        self.title = QLabel(self.page)
        self.title.move(self.margin['left'], self.margin['top'])
        self.title.setText('Plot Violins')
        self.title.setStyleSheet(self.style['title'])
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # ## Input section
        # Input header
        self.input_header = QLabel(self.page)
        self.input_header.move(self.margin['left'], self.widget_vposition(self.title) + 5)
        self.input_header.setText('Load data')
        self.input_header.setStyleSheet(self.style['header'])
        self.input_header.adjustSize()
        # Input/Output frame
        self.input_frame = QFrame(self.page)
        self.input_frame.setGeometry(self.margin['left'],
                                     self.widget_vposition(self.input_header) + 5, 335, 70)
        self.input_frame.setFrameShape(QFrame.StyledPanel)
        self.input_frame.setLayout(QFormLayout())
        # Raw data button
        self.input_button = QPushButton(self.page)
        self.input_button.setStyleSheet(self.style['button'])
        self.set_icon(self.input_button, 'file')
        self.input_button.setObjectName('file')
        self.input_button.setText(' Load raw data file')
        self.input_button.setToolTip('Load raw data file (the file given to SCOUTS as the input file)')
        self.input_button.clicked.connect(self.get_path)
        # SCOUTS results button
        self.output_button = QPushButton(self.page)
        self.output_button.setStyleSheet(self.style['button'])
        self.set_icon(self.output_button, 'folder')
        self.output_button.setObjectName('folder')
        self.output_button.setText(' Load SCOUTS results')
        self.output_button.setToolTip('Load data from SCOUTS analysis '
                                      '(the folder given to SCOUTS as the output folder)')
        self.output_button.clicked.connect(self.get_path)
        # Add widgets above to input frame Layout
        self.input_frame.layout().addRow(self.input_button)
        self.input_frame.layout().addRow(self.output_button)

        # ## Samples section
        # Samples header
        self.samples_header = QLabel(self.page)
        self.samples_header.move(self.margin['left'], self.widget_vposition(self.input_frame) + 5)
        self.samples_header.setText('Select sample names')
        self.samples_header.setStyleSheet(self.style['header'])
        self.samples_header.adjustSize()
        # Samples frame
        self.samples_frame = QFrame(self.page)
        self.samples_frame.setGeometry(self.margin['left'],
                                       self.widget_vposition(self.samples_header) + 5, 335, 80)
        self.samples_frame.setFrameShape(QFrame.StyledPanel)
        self.samples_frame.setLayout(QFormLayout())
        # Samples label
        self.samples_label = QLabel(self.page)
        self.samples_label.setText('Write sample names delimited by semicolons below.\nEx: Control;Treat_01;Pac-03')
        self.samples_label.setStyleSheet(self.style['label'])
        # Sample names line edit
        self.sample_names = QLineEdit(self.page)
        self.samples_label.setStyleSheet(self.style['line edit'])
        # Add widgets above to samples frame Layout
        self.samples_frame.layout().addRow(self.samples_label)
        self.samples_frame.layout().addRow(self.sample_names)

        # ## Analysis section
        # Analysis header
        self.analysis_header = QLabel(self.page)
        self.analysis_header.move(self.margin['left'], self.widget_vposition(self.samples_frame) + 5)
        self.analysis_header.setText('Plot parameters')
        self.analysis_header.setStyleSheet(self.style['header'])
        self.analysis_header.adjustSize()
        # Analysis frame
        self.analysis_frame = QFrame(self.page)
        self.analysis_frame.setGeometry(self.margin['left'],
                                        self.widget_vposition(self.analysis_header) + 5, 335, 140)
        self.analysis_frame.setFrameShape(QFrame.StyledPanel)
        self.analysis_frame.setLayout(QFormLayout())
        # Analysis labels
        self.analysis_label_01 = QLabel(self.page)
        self.analysis_label_01.setText('Compare')
        self.analysis_label_01.setStyleSheet(self.style['label'])
        self.analysis_label_02 = QLabel(self.page)
        self.analysis_label_02.setText('with')
        self.analysis_label_02.setStyleSheet(self.style['label'])
        self.analysis_label_03 = QLabel(self.page)
        self.analysis_label_03.setText('for marker')
        self.analysis_label_03.setStyleSheet(self.style['label'])
        self.analysis_label_04 = QLabel(self.page)
        self.analysis_label_04.setText('Outlier type')
        self.analysis_label_04.setStyleSheet(self.style['label'])
        # Analysis drop-down boxes
        self.drop_down_01 = QComboBox(self.page)
        self.drop_down_01.addItems(['top outliers', 'bottom outliers'])
        self.drop_down_02 = QComboBox(self.page)
        self.drop_down_02.addItems(['whole population', 'non-outliers'])
        self.drop_down_03 = QComboBox(self.page)
        self.drop_down_04 = QComboBox(self.page)
        self.drop_down_04.addItems(['OutS', 'OutR'])
        # Add widgets above to samples frame Layout
        self.analysis_frame.layout().addRow(self.analysis_label_01, self.drop_down_01)
        self.analysis_frame.layout().addRow(self.analysis_label_02, self.drop_down_02)
        self.analysis_frame.layout().addRow(self.analysis_label_03, self.drop_down_03)
        self.analysis_frame.layout().addRow(self.analysis_label_04, self.drop_down_04)

        # Plot button (stand-alone)
        self.plot_button = QPushButton(self.page)
        self.plot_button.setGeometry(self.margin['left'],
                                     self.widget_vposition(self.analysis_frame) + 5, 335, 30)
        self.set_icon(self.plot_button, 'pipe')
        self.plot_button.setText(' Plot')
        self.plot_button.setToolTip('Plot data after loading the input data and selecting parameters')
        self.plot_button.setEnabled(False)
        self.plot_button.clicked.connect(self.run_plot)
        self.secondary_window = QWidget()
        self.secondary_window.resize(720, 720)
        self.dynamic_canvas = DynamicCanvas(self.secondary_window, width=6, height=6, dpi=120)

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

    def get_path(self) -> None:
        """Opens a dialog box and sets the chosen file/folder path, depending on the caller widget."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        func = None
        if self.sender().objectName() == 'file':
            query, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All Files (*)", options=options)
            if query:
                func = self.load_raw_data
            else:
                self.population_df = None
                self.plot_button.setEnabled(False)
        elif self.sender().objectName() == 'folder':
            query = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
            if query:
                func = self.load_scouts_results
            else:
                self.summary_df = None
                self.plot_button.setEnabled(False)
        if func is not None:
            # noinspection PyUnboundLocalVariable
            worker = Worker(func=func, query=query)
            worker.signals.error.connect(self.generic_error_message)
            self.threadpool.start(worker)
            message = QMessageBox(self.page)
            message.setText('Loading...')
            message.show()
            self.threadpool.waitForDone(-1)
            message.close()
            if isinstance(self.summary_df, pd.DataFrame) and isinstance(self.population_df, pd.DataFrame):
                self.plot_button.setEnabled(True)

    def load_raw_data(self, query: str) -> None:
        self.population_df = pd.read_excel(query, index_col=0)
        self.drop_down_03.clear()
        for marker in self.population_df.columns:
            self.drop_down_03.addItem(marker)

    def load_scouts_results(self, query: str) -> None:
        self.summary_df = pd.read_excel(os.path.join(query, 'summary.xlsx'), index_col=None)
        self.summary_path = query

    def run_plot(self) -> None:
        worker = Worker(func=self.plot)
        self.threadpool.start(worker)

    def plot(self) -> None:
        # Clear figure currently on plot
        self.dynamic_canvas.axes.cla()
        # Initialize values and get parameters from GUI
        columns = ['sample', 'marker', 'population', 'expression']
        samples = self.parse_sample_names()
        population = self.drop_down_01.currentText()
        pop_to_analyse = self.drop_down_02.currentText()
        marker = self.drop_down_03.currentText()
        cutoff_from_reference = True if 'reference' in self.drop_down_04.currentText() else False
        violin_df = pd.DataFrame(columns=columns)
        # Start fetching data from files
        # Compare outliers to whole population
        if pop_to_analyse == 'whole population':
            for partial_df in yield_violin_values(df=self.population_df, population='whole population',
                                                  samples=samples, marker=marker, columns=columns):
                violin_df = violin_df.append(partial_df)
        # Compare outliers to non-outlier population
        else:
            for file_number in yield_selected_file_numbers(summary_df=self.summary_df, population='non-outliers',
                                                           cutoff_from_reference=cutoff_from_reference, marker=marker):
                df_path = os.path.join(self.summary_path, 'data', f'{"%04d" % file_number}.csv')
                sample_df = pd.read_csv(df_path, index_col=0)
                for partial_df in yield_violin_values(df=sample_df, population='non-outliers', samples=samples,
                                                      marker=marker, columns=columns):
                    violin_df = violin_df.append(partial_df)
        # Get outlier values
        for file_number in yield_selected_file_numbers(summary_df=self.summary_df, population=population,
                                                       cutoff_from_reference=cutoff_from_reference, marker=marker):
            df_path = os.path.join(self.summary_path, 'data', f'{"%04d" % file_number}.csv')
            sample_df = pd.read_csv(df_path, index_col=0)
            for partial_df in yield_violin_values(df=sample_df, population=population, samples=samples,
                                                  marker=marker, columns=columns):
                violin_df = violin_df.append(partial_df)
        # Plot data
        populations = violin_df.population.unique()
        subset_by_marker = violin_df[violin_df['marker'] == marker]
        for pop in populations:
            subset_by_pop = subset_by_marker.loc[subset_by_marker['population'] == pop]
            color = [0.4, 0.76078431, 0.64705882] if pop != population else [0.98823529, 0.55294118, 0.38431373]
            for sample in samples:
                subset_by_sample = subset_by_pop.loc[subset_by_pop['sample'] == sample]
                sat = 1.0 - samples.index(sample) / (len(samples) + 1)
                self.dynamic_canvas.update_figure(subset_by_sample=subset_by_sample, color=color, sat=sat,
                                                  samples=samples)
        # Draw plotted data on canvas
        self.dynamic_canvas.axes.set_title(f'{marker} expression')
        self.dynamic_canvas.fig.canvas.draw()
        self.secondary_window.show()

    def parse_sample_names(self):
        return self.sample_names.text().split(';')

    def generic_error_message(self, error) -> None:
        trace = traceback.format_exc()
        """Error message box used to display any error message (including traceback) for any uncaught errors."""
        title = 'An error occurred!'
        QMessageBox.critical(self, title, f"{str(error)}\n\nfull traceback:\n{str(trace)}")

    def closeEvent(self, event: QEvent) -> None:
        """Defines the message box for when the user wants to quit SCOUTS."""
        title = 'Quit Violins'
        mes = "Are you sure you want to quit?"
        reply = QMessageBox.question(self, title, mes, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.setEnabled(False)
            self.threadpool.waitForDone()
            event.accept()
        else:
            event.ignore()


def yield_violin_values(df: pd.DataFrame, population: str, samples: List[str], marker: str,
                        columns: List[str]) -> pd.DataFrame:
    """Returns a DataFrame from expression values, along with information of sample, marker and population. This
    DataFrame is appended to the violin plot DataFrame in order to simplify plotting the violins afterwards."""
    for sample in samples:
        series = df.loc[df.index.str.contains(sample)].loc[:, marker]
        yield pd.DataFrame({'sample': sample, 'marker': marker, 'population': population, 'expression': series},
                           columns=columns)


def yield_selected_file_numbers(summary_df: pd.DataFrame, population: str, cutoff_from_reference: bool,
                                marker: str) -> Generator[pd.DataFrame, None, None]:
    """Yields file numbers from DataFrames resulting from SCOUTS analysis. DataFrames are yielded based on
    global values, i.e. the comparisons the user wants to perform."""
    cutoff = 'sample'
    if cutoff_from_reference:
        cutoff = 'reference'
    for index, (file_number, cutoff_from, reference, outliers_for, category) in summary_df.iterrows():
        if cutoff_from == cutoff and outliers_for == marker and category == population:
            yield file_number


class DynamicCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def update_figure(self, subset_by_sample, color, sat, samples):
        sns.violinplot(ax=self.axes, data=subset_by_sample, x='sample', y='expression', color=color, saturation=sat,
                       order=samples)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    violin_gui = ViolinGUI()
    violin_gui.show()
    sys.exit(app.exec_())
