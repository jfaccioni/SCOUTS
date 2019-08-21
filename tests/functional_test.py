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

in_path = '/home/juliano/PycharmProjects/SCOUTS/SCOUTS/test-case/test-case.xlsx'
out_path = '/home/juliano/PycharmProjects/SCOUTS/SCOUTS/test-case/results'

test_dict = {'input_file': in_path,
             'output_folder': out_path,
             'cutoff_rule': 'sample',
             'marker_rule': 'marker',
             'tukey_factor': 1.5,
             'export_csv': False,
             'export_excel': True,
             'single_excel': False,
             'sample_list': [('Yes', 'ct'), ('No', 'treat'), ('No', 'patient')],
             'gate_cutoff': 0.1,
             'non_outliers': True,
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
