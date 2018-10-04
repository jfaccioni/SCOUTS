import sys
import traceback

from PyQt5.QtWidgets import QApplication

import messages
from custom_errors import (ControlNotFound, EmptySampleList, PandasInputError,
                           SampleNamingError)
from scouts import SCOUTS
from scouts_analysis import analyse

CUSTOM_ERRORS = (ControlNotFound, EmptySampleList, PandasInputError,
                 SampleNamingError)

in_path = '/home/juliano/PycharmProjects/SCOUTS/SCOUTS/input-template/mass-cytometry template.xlsx'
out_path = '/home/juliano/Desktop/scouts-out'

test_dict = {'input_file': in_path,
             'output_folder': out_path,
             'cutoff_rule': 'both',
             'by_marker': 'both',
             'tukey': 1.5,
             'export_csv': True,
             'export_excel': True,
             'group_excel': False,
             'sample_list': [('Yes', 'Ct'), ('No', 'RT'), ('No', 'Torin')],
             'gate_cutoff': 0.1,
             'not_outliers': True,
             'bottom_outliers': True}

app = QApplication(sys.argv)
ss = SCOUTS()
try:
    analyse(ss, **test_dict)
except Exception as e:
    if type(e) not in CUSTOM_ERRORS and type(e) != AssertionError:
        trace = traceback.format_exc()
        messages.generic_error_message(ss, trace, e)
else:
    messages.module_done(ss)
