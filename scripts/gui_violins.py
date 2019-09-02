from __future__ import annotations

import os
import sys
from typing import Dict, Generator, TYPE_CHECKING, Tuple

# noinspection PyUnresolvedReferences
from PySide2.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal, Slot
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QDoubleSpinBox, QFileDialog,
                               QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
                               QMessageBox, QPushButton, QRadioButton, QStackedWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)
from src.utils import get_project_root


if TYPE_CHECKING:
    from PySide2.QtCore import QEvent


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
        """ViolinGUI Constructor. Defines all aspects of the GUI."""
        # Inherits from QMainWindow
        super().__init__()
        self.root = get_project_root()
        self.setWindowTitle("Plot Violins")
        self.resize(*self.size.values())
        # Creates QWidget as QMainWindow's central widget
        self.page = QWidget(self)
        self.setCentralWidget(self.page)
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
        self.input_header.setText('Select input')
        self.input_header.setStyleSheet(self.style['header'])
        self.input_header.adjustSize()
        # Input/Output frame
        self.input_frame = QFrame(self.page)
        self.input_frame.setGeometry(self.margin['left'],
                                     self.widget_vposition(self.input_header) + 5, self.rlimit(), 250)
        self.input_frame.setFrameShape(QFrame.StyledPanel)
        self.input_frame.setLayout(QFormLayout())
        # Input data button
        self.input_button = QPushButton(self.input_frame)
        self.input_button.setStyleSheet(self.style['button'])
        self.set_icon(self.input_button, 'file')
        self.input_button.setObjectName('file')
        self.input_button.setText(' Select input file\n(same used for SCOUTS analysis')
        self.input_button.clicked.connect(self.get_path)
        # Input data path box
        self.input_path = QLineEdit(self.input_frame)
        self.input_path.setObjectName('input_path')
        self.input_path.setStyleSheet(self.style['line edit'])
        # SCOUTS output button
        self.output_button = QPushButton(self.input_frame)
        self.output_button.setStyleSheet(self.style['button'])
        self.set_icon(self.output_button, 'folder')
        self.output_button.setObjectName('output')
        self.output_button.setText(' Select output folder\n(same where SCOUTS analysis was saved to)')
        self.output_button.clicked.connect(self.get_path)
        # SCOUTS output path box
        self.output_path = QLineEdit(self.input_frame)
        self.output_path.setStyleSheet(self.style['line edit'])
        # Add widgets above to input frame Layout
        self.input_frame.layout().addRow(self.input_button)
        #self.input_frame.layout().addRow(self.input_path)
        self.input_frame.layout().addRow(self.output_button)
        #self.input_frame.layout().addRow(self.output_path)
        self.input_frame.adjustSize()
        
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
        if self.sender().objectName() == 'input':
            query, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All Files (*)", options=options)
        elif self.sender().objectName() == 'output':
            query = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        else:
            return
        if query:
            self.sender().setText(query)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    violin_gui = ViolinGUI()
    violin_gui.show()
    sys.exit(app.exec_())
