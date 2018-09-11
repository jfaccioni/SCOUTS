import os
from pprint import pprint

import numpy as np
import pandas as pd

from custom_errors import (ControlNotFound, EmptySampleList, PandasInputError,
                           SampleNamingError)

# pandas df options
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('expand_frame_repr', False)


def cytof(widget, input_file, output_folder, cutoff_rule, by_marker, tukey,
          export_csv, export_excel, group_excel, sample_list, gate_cutoff):
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
    if gate_cutoff is not None:
        for index, row in df.iterrows():
            mean_row_value = np.mean(row[1:])
            if mean_row_value < gate_cutoff:
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
            cutoff = (iqr * tukey) + third_quartile
            marker_dict[marker] = (first_quartile, third_quartile, iqr, cutoff)
            sample_dict[sample] = marker_dict
        assert sample_dict, marker_dict
    # change directory to output, open log file
    os.chdir(output_folder)
    if 'log' not in os.listdir(os.getcwd()):
        os.mkdir('log')
    f = open(os.path.join('log', 'outlier_analysis_log.txt'), 'w')
    # iterate over yield_dataframes functions, subsetting dataframes
    # and saving saving them to file as needed
    df_list = []
    for dataframe, m, s, n in yield_dataframes(log=f, df=df,
                                               sample_dict=sample_dict,
                                               control=control,
                                               outliers=cutoff_rule,
                                               by_marker=by_marker):
        if s not in os.listdir(os.getcwd()):
            os.mkdir(s)
        main_name = f'{m}_{s}_cutoff_by_{n}'
        output = os.path.join(s, f'{main_name}')
        if export_csv:
            dataframe.to_csv(f'{output}.csv', index=False)
        if export_excel:
            dataframe.to_excel(f'{output}.xlsx', sheet_name=m, index=False)
            if group_excel:
                df_list.append((dataframe, main_name))
    # close log file
    f.write('\n\n CUTOFF VALUES AS A DICTIONARY:\n')
    pprint(sample_dict, stream=f, width=100)
    f.close()
    # save master excel file
    if df_list:
        writer = pd.ExcelWriter('master_output.xlsx')
        for dataframe, name in df_list:
            dataframe.to_excel(writer, name, index=False)
        writer.save()


def yield_dataframes(log, df, sample_dict, control, outliers, by_marker):
    # outliers by control, outliers by individual markers
    if outliers in ('control', 'both') and by_marker in ('marker', 'both'):
        log.write('------- CUTOFF BY CONTROL, OUTLIERS BY MARKER -------\n\n\n')
        for sample, _ in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, cutoff) in sample_dict[control].items():
                output_df = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df.reset_index(drop=True, inplace=True)
                log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                log.write('METHOD: use control cutoff, ')
                log.write('check outliers for current marker only\n')
                log.write(f'CUTOFF: {cutoff}')
                log.write('\n\n')
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, marker, sample, 'control'
    # outliers by control, outliers by whole row
    if outliers in ('control', 'both') and by_marker in ('row', 'both'):
        log.write('------- CUTOFF BY CONTROL, OUTLIERS BY ROW -------\n\n\n')
        for sample, _ in sample_dict.items():
            log.write(f'SAMPLE: {sample}\n')
            log.write('METHOD: use control cutoff, ')
            log.write('check outliers for any markers in whole row')
            log.write('\n\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            for marker, (*_, cutoff) in sample_dict[control].items():
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            output_df.reset_index(drop=True, inplace=True)
            log.write(str(output_df))
            log.write('\n\n\n\n')
            yield output_df, 'all_markers', sample, 'control'
    # outliers by sample, outliers by individual markers
    if outliers in ('sample', 'both') and by_marker in ('marker', 'both'):
        log.write('------- CUTOFF BY SAMPLE, OUTLIERS BY MARKER -------\n\n\n')
        for sample, mkdict in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, cutoff) in mkdict.items():
                output_df = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df.reset_index(drop=True, inplace=True)
                log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                log.write('METHOD: use sample cutoff, ')
                log.write('check outliers for current marker only\n')
                log.write(f'CUTOFF: {cutoff}')
                log.write('\n\n')
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, marker, sample, 'sample'
    # outliers by control, outliers by whole row
    if outliers in ('sample', 'both') and by_marker in ('row', 'both'):
        log.write('------- CUTOFF BY SAMPLE, OUTLIERS BY ROW -------\n\n\n')
        for sample, mkdict in sample_dict.items():
            log.write(f'SAMPLE: {sample}')
            log.write('METHOD: use sample cutoff, ')
            log.write('check outliers for any markers in whole row')
            log.write('\n\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            for marker, (*_, cutoff) in mkdict.items():
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            output_df.reset_index(drop=True, inplace=True)
            log.write(str(output_df))
            log.write('\n\n\n\n')
            yield output_df, 'all_markers', sample, 'sample'
