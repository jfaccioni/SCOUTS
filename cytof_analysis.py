import os

import numpy as np
import pandas as pd

from ui.custom_errors import (ControlNotFound, EmptySampleList,
                              PandasInputError, SampleNamingError)

# pandas df options
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('expand_frame_repr', False)
# cutoff value for gating
GATE_CUTOFF = 0.1


def cytof(widget, input_file, output_folder, outliers, by_marker, tuckey,
          export_csv, export_excel, group_excel, sample_list):
    # get sample names and control sample
    samples = []
    control = ''
    for sample_type, sample in sample_list:
        if sample_type == 'Yes':
            control = sample
        samples.append(sample)
    # checks if samples were passed on the input table at all
    try:
        assert samples
    except AssertionError:
        raise EmptySampleList
    # checks if there is one sample passed as control
    try:
        assert control
    except AssertionError:
        raise ControlNotFound
    # read input as pandas DataFrame, fails if file has unsupported extension
    if input_file.endswith('.xlsx') or input_file.endswith('xls'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        raise PandasInputError(widget)
    # checks if sample names are part of any string in first row
    for sample in samples:
        try:
            assert any(sample in text for text in list(df.iloc[:, 0]))
        except AssertionError:
            raise SampleNamingError(widget)

    # gate rows
    for index, row in df.iterrows():
        mean_row_value = np.mean(row[1:])
        if mean_row_value < GATE_CUTOFF:
            df = df.drop(index, axis=0)
    df.reset_index(drop=True, inplace=True)
    # build cutoff values
    sample_dict = {}  # dict -> { 'sample' : { 'marker' : (. . .) } }
    for sample in samples:
        marker_dict = {}  # dict -> { 'marker' : (Q1, Q3, IQR, cutoff value) }
        # select rows containing the string stored in "sample"
        filtered_df = df[df[list(df)[0]].str.contains(sample)]  # don't ask!
        quantile_df = filtered_df.quantile([0.25, 0.75])
        for marker in quantile_df:
            first_quartile, third_quartile = quantile_df[marker]
            iqr = third_quartile - first_quartile
            cutoff = (iqr * tuckey) + third_quartile
            marker_dict[marker] = (first_quartile, third_quartile, iqr, cutoff)
            sample_dict[sample] = marker_dict
        assert sample_dict, marker_dict
    # open log file
    f = open(os.path.join(output_folder, 'log.txt'), 'w')
    # outliers by control, outliers by individual markers
    f.write('\n\n\n ---------- BY CONTROL, BY MARKER ----------\n\n\n')
    if outliers in ('control', 'both') and by_marker in ('marker', 'both'):
        for sample, _ in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, cutoff) in sample_dict[control].items():
                output_df = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df.reset_index(drop=True, inplace=True)
                f.write(f'CURRENT MARKER: {marker}\nCURRENT SAMPLE: {sample}\n')
                f.write('METHOD: use control cutoff, ')
                f.write('check outliers for current marker only')
                f.write('\n\n')
                f.write(str(output_df))
                f.write('\n\n\n\n')
    # outliers by control, outliers by whole row
    f.write('\n\n\n ---------- BY CONTROL, BY ROW ----------\n\n\n')
    if outliers in ('control', 'both') and by_marker in ('row', 'both'):
        for sample, _ in sample_dict.items():
            f.write(f'CURRENT SAMPLE: {sample}\n')
            f.write('METHOD: use control cutoff, ')
            f.write('check outliers for any markers in whole row')
            f.write('\n\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            for marker, (*_, cutoff) in sample_dict[control].items():
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            output_df.reset_index(drop=True, inplace=True)
            f.write(str(output_df))
            f.write('\n\n\n\n')
    # outliers by sample, outliers by individual markers
    f.write('\n\n\n ---------- BY SAMPLE, BY MARKER ----------\n\n\n')
    if outliers in ('sample', 'both') and by_marker in ('marker', 'both'):
        for sample, mkdict in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, cutoff) in mkdict.items():
                output_df = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df.reset_index(drop=True, inplace=True)
                f.write(f'CURRENT MARKER: {marker}\nCURRENT SAMPLE: {sample}\n')
                f.write('METHOD: use sample cutoff, ')
                f.write('check outliers for current marker only')
                f.write('\n\n')
                f.write(str(output_df))
                f.write('\n\n\n\n')
    # outliers by control, outliers by whole row
    f.write('\n\n\n ---------- BY SAMPLE, BY ROW ----------\n\n\n')
    if outliers in ('sample', 'both') and by_marker in ('row', 'both'):
        for sample, mkdict in sample_dict.items():
            f.write(f'CURRENT SAMPLE: {sample}')
            f.write('METHOD: use sample cutoff, ')
            f.write('check outliers for any markers in whole row')
            f.write('\n\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            for marker, (*_, cutoff) in mkdict.items():
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            output_df.reset_index(drop=True, inplace=True)
            f.write(str(output_df))
            f.write('\n\n\n\n')
    # close log file
    f.close()
