from __future__ import annotations

from os.path import join
from sys import argv, exit as sys_exit
from traceback import format_exc
from typing import Callable, Generator, List, TYPE_CHECKING, Tuple

from PySide2.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal, Slot
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QFormLayout, QFrame, QLabel,
                               QLineEdit, QMainWindow, QMessageBox, QPushButton, QSizePolicy, QWidget)
from matplotlib import use as set_backend
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavBar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from pandas import DataFrame, read_csv, read_excel
from seaborn import set as set_style, violinplot

if TYPE_CHECKING:
    from PySide2.QtCore import QEvent

set_backend('Qt5Agg')
set_style(style="whitegrid")


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
        self.set_icon(self.input_button, 'x-office-spreadsheet')
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
        self.drop_down_01.addItems(['whole population', 'non-outliers', 'top outliers', 'bottom outliers', 'none'])
        self.drop_down_01.setCurrentIndex(2)
        self.drop_down_02 = QComboBox(self.page)
        self.drop_down_02.addItems(['whole population', 'non-outliers', 'top outliers', 'bottom outliers', 'none'])
        self.drop_down_02.setCurrentIndex(0)
        self.drop_down_03 = QComboBox(self.page)
        self.drop_down_04 = QComboBox(self.page)
        self.drop_down_04.addItems(['OutS', 'OutR'])
        # Add widgets above to samples frame Layout
        self.analysis_frame.layout().addRow(self.analysis_label_01, self.drop_down_01)
        self.analysis_frame.layout().addRow(self.analysis_label_02, self.drop_down_02)
        self.analysis_frame.layout().addRow(self.analysis_label_03, self.drop_down_03)
        self.analysis_frame.layout().addRow(self.analysis_label_04, self.drop_down_04)

        self.legend_checkbox = QCheckBox(self.page)
        self.legend_checkbox.setGeometry(self.margin['left'],
                                         self.widget_vposition(self.analysis_frame) + 5, 335, 30)
        self.legend_checkbox.setText('Add legend to the plot')

        # Plot button (stand-alone)
        self.plot_button = QPushButton(self.page)
        self.plot_button.setGeometry(self.margin['left'],
                                     self.widget_vposition(self.legend_checkbox) + 5, 335, 30)
        self.set_icon(self.plot_button, 'system-run')
        self.plot_button.setText(' Plot')
        self.plot_button.setToolTip('Plot data after loading the input data and selecting parameters')
        self.plot_button.setEnabled(False)
        self.plot_button.clicked.connect(self.run_plot)

        # ## Secondary Window
        # This is used to plot the violins only
        self.secondary_window = QMainWindow(self)
        self.secondary_window.resize(720, 720)
        self.dynamic_canvas = DynamicCanvas(self.secondary_window, width=6, height=6, dpi=120)
        self.secondary_window.setCentralWidget(self.dynamic_canvas)
        self.secondary_window.addToolBar(NavBar(self.dynamic_canvas, self.secondary_window))

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

    @staticmethod
    def set_icon(widget: QWidget, icon: str) -> None:
        """Associates an icon to a widget."""
        i = QIcon()
        i.addPixmap(QPixmap(join('default_icons', f'{icon}.svg')))
        widget.setIcon(QIcon.fromTheme(icon, i))

    def get_path(self) -> None:
        """Opens a dialog box and sets the chosen file/folder path, depending on the caller widget."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        query = None
        func = None
        if self.sender().objectName() == 'file':
            query, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All Files (*)", options=options)
            func = self.load_raw_data
        elif self.sender().objectName() == 'folder':
            query = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
            func = self.load_scouts_results
        if query:
            self.load_data(query, func)

    def load_data(self, query: str, func: Callable) -> None:
        """str"""  # TODO
        worker = Worker(func=func, query=query)
        message = self.loading_message()
        worker.signals.started.connect(message.show)
        worker.signals.started.connect(self.page.setDisabled)
        worker.signals.error.connect(self.generic_error_message)
        worker.signals.failed.connect(self.plot_button.setDisabled)
        worker.signals.success.connect(message.destroy)
        worker.signals.success.connect(self.enable_plot)
        worker.signals.finished.connect(self.page.setEnabled)
        self.threadpool.start(worker)

    def loading_message(self) -> QDialog:
        """str"""  # TODO
        message = QDialog(self)
        message.setWindowTitle('Loading')
        message.resize(300, 50)
        label = QLabel('loading DataFrame into memory...', message)
        label.setStyleSheet(self.style['label'])
        label.adjustSize()
        label.setAlignment(Qt.AlignCenter)
        label.move(int((message.width() - label.width())/2), int((message.height() - label.height())/2))
        return message

    def load_raw_data(self, query: str) -> None:
        """str"""  # TODO
        self.population_df = read_excel(query, index_col=0)
        self.drop_down_03.clear()
        self.drop_down_03.addItems(list(self.population_df.columns))
        self.drop_down_03.setCurrentIndex(0)

    def load_scouts_results(self, query: str) -> None:
        """str"""  # TODO
        self.summary_df = read_excel(join(query, 'summary.xlsx'), index_col=None)
        self.summary_path = query

    def enable_plot(self) -> None:
        if isinstance(self.summary_df, DataFrame) and isinstance(self.population_df, DataFrame):
            self.plot_button.setEnabled(True)

    def run_plot(self) -> None:
        """str"""  # TODO
        worker = Worker(func=self.plot)
        worker.signals.error.connect(self.generic_error_message)
        worker.signals.success.connect(self.secondary_window.show)
        self.threadpool.start(worker)

    def plot(self) -> None:
        """str"""  # TODO
        # Clear figure currently on plot
        self.dynamic_canvas.axes.cla()
        # Initialize values and get parameters from GUI
        columns = ['sample', 'marker', 'population', 'expression']
        samples = self.parse_sample_names()
        pop_01 = self.drop_down_01.currentText()
        pop_02 = self.drop_down_02.currentText()
        pops_to_analyse = [pop_01, pop_02]
        marker = self.drop_down_03.currentText()
        cutoff_from_reference = True if self.drop_down_04.currentText() == 'OutR' else False
        violin_df = DataFrame(columns=columns)
        # Start fetching data from files
        # Whole population
        for pop in pops_to_analyse:
            if pop == 'whole population':
                for partial_df in self.yield_violin_values(df=self.population_df, population='whole population',
                                                           samples=samples, marker=marker, columns=columns):
                    violin_df = violin_df.append(partial_df)
        # Other comparisons
            elif pop != 'none':
                for file_number in self.yield_selected_file_numbers(summary_df=self.summary_df, population=pop,
                                                                    cutoff_from_reference=cutoff_from_reference,
                                                                    marker=marker):
                    df_path = join(self.summary_path, 'data', f'{"%04d" % file_number}.csv')
                    sample_df = read_csv(df_path, index_col=0)
                    if not sample_df.empty:
                        for partial_df in self.yield_violin_values(df=sample_df, population=pop, samples=samples,
                                                                   marker=marker, columns=columns):
                            violin_df = violin_df.append(partial_df)
        # Plot data
        pops_to_analyse = [p for p in pops_to_analyse if p != 'none']
        violin_df = violin_df[violin_df['marker'] == marker]
        for pop in pops_to_analyse:
            pop_subset = violin_df.loc[violin_df['population'] == pop]
            for sample in samples:
                sample_subset = pop_subset.loc[pop_subset['sample'] == sample]
                sat = 1.0 - samples.index(sample) / (len(samples) + 1)
                self.dynamic_canvas.update_figure(subset_by_sample=sample_subset, pop=pop, sat=sat, samples=samples)
        # Draw plotted data on canvas
        if self.legend_checkbox.isChecked():
            self.dynamic_canvas.add_legend()
        self.dynamic_canvas.axes.set_title(f'{marker} expression - {self.drop_down_04.currentText()}')
        self.dynamic_canvas.fig.canvas.draw()

    def parse_sample_names(self):
        """str"""  # TODO
        return self.sample_names.text().split(';')

    def generic_error_message(self, error: Tuple[Exception, str]) -> None:
        """Error message box used to display any error message (including traceback) for any uncaught errors."""
        name, trace = error
        QMessageBox.critical(self, 'An error occurred!', f"Error: {str(name)}\n\nfull traceback:\n{trace}")

    def closeEvent(self, event: QEvent) -> None:
        """Defines the message box for when the user wants to quit SCOUTS."""
        title = 'Quit Application'
        mes = "Are you sure you want to quit?"
        reply = QMessageBox.question(self, title, mes, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.setEnabled(False)
            self.threadpool.waitForDone()
            event.accept()
        else:
            event.ignore()

    def debug(self):
        """str"""  # TODO
        laptop = False
        repo = "SCOUTS"
        if laptop:
            repo = "scouts"
        path = f'/home/juliano/Repositories/my-github-repositories/{repo}/local/sample data/cytof gio/'
        self.load_raw_data(join(path, 'gio-mass-cytometry.xlsx'))
        self.load_scouts_results(join(path, 'scouts output'))
        self.sample_names.setText('Ct;RT;Torin')
        self.plot_button.setEnabled(True)

    @staticmethod
    def yield_violin_values(df: DataFrame, population: str, samples: List[str], marker: str,
                            columns: List[str]) -> DataFrame:
        """Returns a DataFrame from expression values, along with information of sample, marker and population. This
        DataFrame is appended to the violin plot DataFrame in order to simplify plotting the violins afterwards."""
        for sample in samples:
            series = df.loc[df.index.str.contains(sample)].loc[:, marker]
            yield DataFrame({'sample': sample, 'marker': marker, 'population': population, 'expression': series},
                            columns=columns)

    @staticmethod
    def yield_selected_file_numbers(summary_df: DataFrame, population: str, cutoff_from_reference: bool,
                                    marker: str) -> Generator[DataFrame, None, None]:
        """Yields file numbers from DataFrames resulting from SCOUTS analysis. DataFrames are yielded based on
        global values, i.e. the comparisons the user wants to perform."""
        cutoff = 'sample'
        if cutoff_from_reference is True:
            cutoff = 'reference'
        for index, (file_number, cutoff_from, reference, outliers_for, category) in summary_df.iterrows():
            if cutoff_from == cutoff and outliers_for == marker and category == population:
                yield file_number


class DynamicCanvas(FigureCanvas):
    colors = {
              'top outliers':     [0.988, 0.553, 0.384],  # green
              'bottom outliers':  [0.259, 0.455, 0.643],  # blue
              'non-outliers':     [0.400, 0.761, 0.647],  # orange
              'whole population': [0.600, 0.600, 0.600]   # gray
    }
    """str"""  # TODO
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_figure(self, subset_by_sample, pop, sat, samples):
        """str"""  # TODO
        color = self.colors[pop]
        violinplot(ax=self.axes, data=subset_by_sample, x='sample', y='expression', color=color, saturation=sat,
                   order=samples)

    def add_legend(self):
        """str"""  # TODO
        labels = {name: Line2D([], [], color=color, marker='s', linestyle='None')
                  for name, color in self.colors.items()}
        self.axes.legend(labels.values(), labels.keys(), fontsize=8)


class Worker(QRunnable):
    """Worker thread for loading DataFrames and generating plots. Avoids unresponsive GUI."""
    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        """Runs the Worker thread."""
        self.signals.started.emit(True)
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as error:
            trace = format_exc()
            self.signals.error.emit((error, trace))
            self.signals.failed.emit()
        else:
            self.signals.success.emit()
        finally:
            self.signals.finished.emit(True)


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread. Supported signals are:
       Started: Worker has started its job. Emits a boolean.
       Error: an Exception was raised. Emits a tuple containing an Exception object and the traceback as a string.
       Failed: Worker has not finished its job due to an error. Nothing is emitted.
       Success: Worker has finished executing without errors. Nothing is emitted.
       Finished: Worker has stopped working (either naturally or by raising an Exception). Emits a boolean."""
    started = Signal(bool)
    error = Signal(Exception)
    failed = Signal()
    success = Signal()
    finished = Signal(bool)


DEBUG = False


def main():
    app = QApplication(argv)
    violin_gui = ViolinGUI()
    if DEBUG:
        violin_gui.debug()
    violin_gui.show()
    sys_exit(app.exec_())
